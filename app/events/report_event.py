import logging
from fastapi_utilities import repeat_at
from app.services.report_service import ReportService
from app.services.store_service import StoreSyncService

logger = logging.getLogger(__name__)

@repeat_at(cron="5 * * * *")
async def processing_data_with_cron_updated_kashio():
    logger.info("-----------------------------------------------------------------")
    logger.info("iniciando el proceso programado (fastapi_utilities event) de extraccion del reporte a las 6:00 am.")
    logger.info("-----------------------------------------------------------------")
    try:
        service = ReportService()
        records = service.fetch_and_parse_report()
        logger.info(f"extraccion finalizada correctamente. {len(records)} registros encontrados en excel.")
        
        # sincronizamos con bd
        sync_svc = StoreSyncService()
        sync_svc.sync_stores(records)
        
    except Exception as e:
        logger.error(f"error durante la tarea programada: {e}")
