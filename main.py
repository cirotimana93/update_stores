import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.routes import router
from app.core.config import Config
from app.core.config import settings

# ajustamos log level para ver la salida
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# importamos el evento
from app.events.report_event import processing_data_with_cron_updated_kashio

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("aplicacion iniciada.")
    
    if settings.DEBUG == False:
        logger.info("modo produccion detectado (debug=false). inicializando cron/eventos en background...")
        # llamamos la funcion asincrona principal para registrar el evento regular
        await processing_data_with_cron_updated_kashio()
    else:
        logger.info("modo development (debug=true). las tareas automaticas estan deshabilitadas.")
        
    yield
    
    logger.info("apagando aplicacion.")

app = FastAPI(title="Servicio Extractor Cajas", lifespan=lifespan)

# registrar rutas
app.include_router(router, prefix="/api/v1")

@app.get("/health")
def health():
    return {"status": "alive"}
