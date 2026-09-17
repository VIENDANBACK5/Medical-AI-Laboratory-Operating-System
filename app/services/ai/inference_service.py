import json
import os
import time
import uuid
import threading
from typing import Dict, Any, Optional
import numpy as np
import torch

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.model_mask import Mask
from app.models.model_volume import Volume
from app.services.ai.manager import AIEngineManager
from app.services.srv_base import BaseService


class AIInferenceService(BaseService[Mask]):
    def __init__(self):
        super().__init__(Mask)
        self.manager = AIEngineManager()
        
        # Thread-safe in-memory task tracker
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.tasks_lock = threading.Lock()
        
        # Storage folder setup
        self.storage_dir = os.path.join(settings.BASE_DIR, "storage")
        self.masks_dir = os.path.join(self.storage_dir, "masks")
        self.tasks_dir = os.path.join(self.storage_dir, "tasks")
        os.makedirs(self.masks_dir, exist_ok=True)
        os.makedirs(self.tasks_dir, exist_ok=True)

    def _save_task_to_disk(self, task_id: str, task_data: Dict[str, Any]) -> None:
        """Persists task state to JSON on disk for resilience across process restarts."""
        try:
            task_file = os.path.join(self.tasks_dir, f"{task_id}.json")
            temp_file = f"{task_file}.tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(task_data, f, indent=2)
            os.replace(temp_file, task_file)
        except Exception:
            pass  # Non-blocking if file write fails

    def _load_task_from_disk(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Recovers task state from JSON file on disk if missing from memory."""
        task_file = os.path.join(self.tasks_dir, f"{task_id}.json")
        if os.path.exists(task_file):
            try:
                with open(task_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return None
        return None

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Query status parameters for a queued background inference task."""
        with self.tasks_lock:
            if task_id in self.tasks:
                return dict(self.tasks[task_id])
        
        # Fallback to persistent disk storage
        disk_task = self._load_task_from_disk(task_id)
        if disk_task:
            with self.tasks_lock:
                self.tasks[task_id] = disk_task
            return disk_task
        return None

    def _update_task(self, task_id: str, updates: Dict[str, Any]) -> None:
        """Helper to safely update memory state and mirror to disk."""
        with self.tasks_lock:
            if task_id in self.tasks:
                self.tasks[task_id].update(updates)
                task_copy = dict(self.tasks[task_id])
            else:
                self.tasks[task_id] = updates
                task_copy = dict(updates)
        self._save_task_to_disk(task_id, task_copy)

    def queue_inference(self, volume_id: int, model_name: str) -> str:
        """Initializes a new task tracking ticket and queues it for async execution."""
        task_id = str(uuid.uuid4())
        initial_state = {
            "task_id": task_id,
            "status": "PENDING",
            "progress": 0,
            "volume_id": volume_id,
            "model_name": model_name,
            "error": None,
            "result_id": None,
            "created_at": time.time(),
        }
        with self.tasks_lock:
            self.tasks[task_id] = initial_state
        self._save_task_to_disk(task_id, initial_state)
        return task_id

    def run_inference_task(self, task_id: str, volume_id: int, model_name: str) -> None:
        """Asynchronous execution task entrypoint running on FastAPI BackgroundTasks."""
        # Update status to RUNNING
        self._update_task(task_id, {"status": "RUNNING", "progress": 10})

        try:
            # 1. Fetch volume details using direct session to support non-HTTP thread contexts
            with SessionLocal() as session:
                volume = session.query(Volume).get(volume_id)
                if not volume:
                    raise FileNotFoundError(f"Volume record {volume_id} not found in database.")

                # Update progress
                self._update_task(task_id, {"progress": 30})

                # Load volume matrix from disk
                npy_path = os.path.join(settings.BASE_DIR, volume.file_path)
                if not os.path.exists(npy_path):
                    raise FileNotFoundError(f"Voxel grid file not found at {npy_path}")
                
                volume_array = np.load(npy_path)

                # volume.spacing is stored in SimpleITK x,y,z order [dx, dy, dz].
                # The voxel array is in numpy z,y,x order, so reverse the spacing
                # to [dz, dy, dx] so it lines up with the array axes the plugin sees.
                spacing = tuple(reversed(volume.spacing))  # [dz, dy, dx]

                # 2. Retrieve AI Plugin
                plugin = self.manager.get_plugin(model_name)
                self._update_task(task_id, {"progress": 50})

                # Lazy-load weights
                plugin.initialize()

                # 3. Predict & Telemetry benchmark
                start_time = time.time()
                
                # Check VRAM if running on CUDA
                vram_start = torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
                
                # Run prediction forward pass
                mask_array = plugin.predict(volume_array, spacing)
                
                duration = time.time() - start_time
                vram_end = torch.cuda.memory_allocated() if torch.cuda.is_available() else 0
                vram_consumed = max(0.0, (vram_end - vram_start) / (1024 * 1024))  # Convert bytes to MB

                self._update_task(task_id, {"progress": 80})

                # 4. Save resulting segmentation matrix to disk
                mask_uuid = str(uuid.uuid4())
                mask_file_path = os.path.join(self.masks_dir, f"{mask_uuid}.npy")
                np.save(mask_file_path, mask_array)

                # 5. Insert Mask database record
                mask_record = Mask(
                    volume_id=volume_id,
                    model_name=plugin.get_info().name,
                    model_version=plugin.get_info().version,
                    file_path=os.path.relpath(mask_file_path, settings.BASE_DIR),
                    inference_time_sec=duration,
                    vram_consumed_mb=vram_consumed,
                    meta_info={"labels": plugin.get_info().labels}
                )
                session.add(mask_record)
                session.commit()
                session.refresh(mask_record)

                # Update status to SUCCESS
                self._update_task(task_id, {
                    "status": "SUCCESS",
                    "progress": 100,
                    "result_id": mask_record.id,
                    "inference_time_sec": duration,
                    "vram_consumed_mb": vram_consumed,
                })

        except Exception as e:
            # Capture error details and mark task as FAILED
            import traceback
            traceback.print_exc()
            self._update_task(task_id, {
                "status": "FAILED",
                "progress": 100,
                "error": str(e),
            })
