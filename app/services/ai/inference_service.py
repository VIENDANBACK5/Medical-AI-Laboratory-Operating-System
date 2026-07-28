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
        os.makedirs(self.masks_dir, exist_ok=True)

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Query status parameters for a queued background inference task."""
        with self.tasks_lock:
            return self.tasks.get(task_id)

    def queue_inference(self, volume_id: int, model_name: str) -> str:
        """Initializes a new task tracking ticket and queues it for async execution."""
        task_id = str(uuid.uuid4())
        with self.tasks_lock:
            self.tasks[task_id] = {
                "status": "PENDING",
                "progress": 0,
                "volume_id": volume_id,
                "model_name": model_name,
                "error": None,
                "result_id": None,
            }
        return task_id

    def run_inference_task(self, task_id: str, volume_id: int, model_name: str) -> None:
        """Asynchronous execution task entrypoint running on FastAPI BackgroundTasks."""
        # Update status to RUNNING
        with self.tasks_lock:
            if task_id in self.tasks:
                self.tasks[task_id]["status"] = "RUNNING"
                self.tasks[task_id]["progress"] = 10

        try:
            # 1. Fetch volume details using direct session to support non-HTTP thread contexts
            with SessionLocal() as session:
                volume = session.query(Volume).get(volume_id)
                if not volume:
                    raise FileNotFoundError(f"Volume record {volume_id} not found in database.")

                # Update progress
                with self.tasks_lock:
                    self.tasks[task_id]["progress"] = 30

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
                
                with self.tasks_lock:
                    self.tasks[task_id]["progress"] = 50

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

                with self.tasks_lock:
                    self.tasks[task_id]["progress"] = 80

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
                with self.tasks_lock:
                    self.tasks[task_id]["status"] = "SUCCESS"
                    self.tasks[task_id]["progress"] = 100
                    self.tasks[task_id]["result_id"] = mask_record.id

        except Exception as e:
            # Capture error details and mark task as FAILED
            import traceback
            traceback.print_exc()
            with self.tasks_lock:
                if task_id in self.tasks:
                    self.tasks[task_id]["status"] = "FAILED"
                    self.tasks[task_id]["progress"] = 100
                    self.tasks[task_id]["error"] = str(e)
