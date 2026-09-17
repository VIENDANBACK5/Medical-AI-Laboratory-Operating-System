import logging
from contextlib import asynccontextmanager

from fastapi.exceptions import ValidationException
import uvicorn
from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware
from starlette.middleware.cors import CORSMiddleware

from app.core.router import router
from app.models import Base
from app.core.database import engine
from app.core.config import settings
from app.utils.exception_handler import (
    CustomException,
    fastapi_error_handler,
    validation_exception_handler,
    custom_error_handler,
)

logging.config.fileConfig(settings.LOGGING_CONFIG_FILE, disable_existing_loggers=False)
logger = logging.getLogger(__name__)
Base.metadata.create_all(bind=engine)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: warm up AI Engine Manager on startup."""
    from app.services.ai.manager import AIEngineManager
    manager = AIEngineManager()
    plugin_names = list(manager.plugins.keys())
    logger.info(f"[MedAI-OS] AI Engine ready — {len(plugin_names)} plugin(s): {plugin_names}")
    yield
    logger.info("[MedAI-OS] Shutting down.")


def get_application() -> FastAPI:
    application = FastAPI(
        title=settings.PROJECT_NAME,
        docs_url="/docs",
        redoc_url="/re-docs",
        openapi_url=f"{settings.API_PREFIX}/openapi.json",
        description="""
## MedAI-OS — Medical AI Laboratory Operating System

An end-to-end modular research platform for 3D medical imaging (DICOM/NIfTI),
deep learning segmentation, computational geometry, and AI implant synthesis.

### Core Capabilities
- **DICOM/NIfTI Ingestion**: Upload and resample volumetric CT scans
- **Plugin AI Engine**: Plug-and-play segmentation (TotalSegmentator, MONAI, MedSAM, Mock)
- **3D Geometry Pipeline**: Marching Cubes → Smoothing → Decimation → Watertight Mesh
- **AI Implant Synthesis**: Bilateral symmetry mirroring and generative shape completion
- **Research SDK**: Standardized Dice/HD95/Chamfer benchmarking and experiment reporting
        """,
        version="2.0.0",
        contact={"name": "MedAI-OS Research Team", "url": "https://github.com/VIENDANBACK5/Medical-AI-Laboratory-Operating-System"},
        license_info={"name": "MIT"},
        debug=settings.DEBUG,
        lifespan=lifespan,
        swagger_ui_init_oauth={
            "clientId": settings.KEYCLOAK_CLIENT_ID,
            "scopes": {"openid": "OpenID Connect scope"},
        },
        swagger_ui_parameters={
            "docExpansion": "none",
            "defaultModelsExpandDepth": -1,
        },
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_middleware(DBSessionMiddleware, db_url=settings.DATABASE_URL)
    application.include_router(router, prefix=settings.API_PREFIX)
    application.add_exception_handler(CustomException, custom_error_handler)
    application.add_exception_handler(ValidationException, validation_exception_handler)
    application.add_exception_handler(Exception, fastapi_error_handler)

    return application


app = get_application()
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=settings.DEBUG)
