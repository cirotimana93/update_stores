from fastapi import APIRouter, HTTPException
from app.services.report_service import ReportService
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/report/cajas")
def get_report_cajas():
    # endpoint manual para descargar y parsear
    # el reporte de cajas desde la gestion de apuestatotal
    logger.info("iniciando ejecucion manual para el reporte de cajas")
    try:
        service = ReportService()
        records = service.fetch_and_parse_report()
        return {"status": "success", "total_records": len(records), "data": records}
    except Exception as e:
        logger.error(f"error en get_report_cajas: {e}")
        raise HTTPException(status_code=500, detail=str(e))
