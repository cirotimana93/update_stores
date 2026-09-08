import io
import pandas as pd
from datetime import datetime, timedelta
import logging
from app.adapters.http_client import HttpClient
from app.core.config import settings

logger = logging.getLogger(__name__)

class ReportService:
    def __init__(self):
        self.http_client = HttpClient(headers=settings.headers)
        
    def fetch_and_parse_report(self) -> list[dict]:
        # fecha actual en caso no se proporcione (siempre de d-1)
        yesterday = datetime.now() - timedelta(days=1)
        date_str = yesterday.strftime("%Y-%m-%d")
        
        payload = {
            "fecha_inicio": date_str,
            "fecha_fin": date_str,
            "group_by": "day"
        }
        
        logger.info(f"iniciando peticion de reporte de cajas para las fechas: {date_str}")
        
        # peticion post
        # retorna 302 hacia el archivo excel (.xls)
        post_response = self.http_client.post(
            url=settings.fastreport_cajas_url,
            data=payload,
            allow_redirects=False
        )
        
        # verificamos si hemos obtenido una url de location para descargar
        location = post_response.headers.get("Location")
        
        if not location:
            logger.warning("no se enonctro la cabecera 'location' en la respuesta. \
                           procedemos a intentar obtener desde el content asumiendo auto-redirect")
            excel_content = post_response.content
        else:
            # comprobamos si el location devuelto es relativo o absoluto
            download_url = f"{settings.base_url}{location}" if location.startswith("/") else location
            logger.info(f"descargando archivo excel desde: {download_url}")
            
            get_response = self.http_client.get(download_url)
            excel_content = get_response.content
            
        return self._parse_excel(excel_content)
        
    def _parse_excel(self, excel_content: bytes) -> list[dict]:
        logger.info("parseando el archivo excel con pd.read_excel (ignorando posible corrupcion)")
        try:
            # el engine 'xlrd' lee correctamente archivos .xls antiguos
            # usamos engine_kwargs para saltar la validacion corrupta
            df = pd.read_excel(io.BytesIO(excel_content), engine="xlrd", engine_kwargs={"ignore_workbook_corruption": True})
        except Exception as e:
            logger.error(f"error parseando binariamente: {e}.")
            raise
                
        try:
            # columnas solicitadas a extraer
            required_columns = ["Centro de Costo", "Local"]
            
            # asegurarse de no fallar si las columnas no tienen formato esperado exacto (ej. espacios)
            available_columns = df.columns.tolist()
            
            final_columns = []
            for req_col in required_columns:
                if req_col in available_columns:
                    final_columns.append(req_col)
            
            if not final_columns:
                logger.error(f"no se encontraron las columnas esperadas {required_columns}. disponibles: {available_columns}")
                # opcional: retornar todas temporalmente si no hay match exacto
                return []
                
            # crear copia para evitar warnings al modificar datos
            reduced_df = df[final_columns].copy()
            
            # excluir la fila de "suma total" y tiendas de prueba de capacitacion
            if "Local" in reduced_df.columns:
                reduced_df = reduced_df[~reduced_df["Local"].astype(str).str.contains("Suma Total", na=False, case=False)]
                # devct: se excluye tienda de prueba de capacitacion
                reduced_df = reduced_df[~reduced_df["Local"].astype(str).str.strip().str.lower().str.contains("capacitaci", na=False)]
            
            # formatear "centro de costo" eliminando el ".0" tratandolo como string o string vacio
            if "Centro de Costo" in reduced_df.columns:
                def format_cost(val):
                    if pd.isna(val) or val == "":
                        return ""
                    try:
                        return str(int(float(val)))
                    except ValueError:
                        return str(val).strip()
                
                reduced_df["Centro de Costo"] = reduced_df["Centro de Costo"].apply(format_cost)
            
            # limpiar datos nulos restantes
            reduced_df = reduced_df.fillna("")
            
            records = reduced_df.to_dict(orient="records")
            logger.info(f"parseo completado con {len(records)} registros extraidos.")
            
            return records
            
        except Exception as e:
            logger.error(f"error obteniendo o filtrando columnas del excel: {e}")
            raise
