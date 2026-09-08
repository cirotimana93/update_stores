import json
import logging
from datetime import datetime, timezone
from sqlalchemy import select, func
from app.core.database import SessionLocal
from app.models import TblStore

logger = logging.getLogger(__name__)

class StoreSyncService:
    def sync_stores(self, report_data: list[dict]):
        logger.info(f"iniciando sincronizacion en bd con {len(report_data)} tiendas obtenidas del excel.")
        
        # limpiamos y armamos un diccionario del json por ceco
        excel_dict = {}
        for row in report_data:
            ceco = str(row.get("Centro de Costo", "")).strip()
            local_name = str(row.get("Local", "")).strip()
            cleanName = local_name.strip().lower()
            # devct: se omite tienda de prueba de capacitacion
            if "capacitaci" in cleanName:
                continue
            if ceco:
                excel_dict[ceco] = local_name

        with SessionLocal() as db:
            # traer todas las tiendas validas de una vez
            # asi evitamos golpear la db multiplicadas veces
            stmt_all = select(TblStore).where(func.upper(TblStore.name).not_like('%AGENTE AT%'))
            all_db_stores = db.scalars(stmt_all).all()
            
            # separar internamente activos y borrados
            db_active_dict = {
                str(store.ceco).strip(): store 
                for store in all_db_stores 
                if store.delete_at is None
            }
            
            db_deleted_dict = {
                str(store.ceco).strip(): store 
                for store in all_db_stores 
                if store.delete_at is not None
            }

            stats_updated_active = 0
            stats_inserted_or_restored = 0
            stats_status_2 = 0

            current_time = datetime.now(timezone.utc)

            # --- escenarios 1 y 2 ---
            # recorremos la fuente de verdad del json
            for excel_ceco, excel_local in excel_dict.items():
                if excel_ceco in db_active_dict:
                    # existio en consulta activa (escenario 1)
                    store = db_active_dict[excel_ceco]
                    store.name = excel_local
                    if store.status != 1:
                        store.status = 1
                        logger.info(f"tienda cambiada a status 1 - ceco: {store.ceco} | nombre: {store.name}")
                    store.updated_at = current_time
                    store.delete_at = None
                    stats_updated_active += 1
                else:
                    # no existe en activos (escenario 2)
                    if excel_ceco in db_deleted_dict:
                        # estaba en borrados, restauramos
                        store = db_deleted_dict[excel_ceco]
                        store.name = excel_local
                        store.status = 1
                        store.delete_at = None
                        store.updated_at = current_time
                        stats_inserted_or_restored += 1
                        logger.info(f"tienda restaurada con status 1 - ceco: {store.ceco} | nombre: {store.name}")
                    else:
                        # no existe para nada en bd, insertamos
                        supervisor_val = json.dumps({
                            "name": "Detectado Ceco",
                            "phone": 999999999,
                            "area_manager": "Generado Automatico",
                            "zone": "Tienda AT",
                            "subzone": 1,
                            "connection_user": "o1subz1fg"
                        }, ensure_ascii=False)
                        
                        newStore = TblStore(
                            name=excel_local,
                            ceco=excel_ceco,
                            supervisor=supervisor_val,
                            company_id=1,
                            status=1,
                            created_at=current_time,
                            updated_at=current_time,
                            delete_at=None
                        )
                        db.add(newStore)
                        stats_inserted_or_restored += 1
                        logger.info(f"tienda nueva insertada con status 1 - ceco: {newStore.ceco} | nombre: {newStore.name}")

            # --- escenario 3 ---
            # devct: se registra en logs cada tienda que no llego en el reporte y cambia a status 2
            for db_ceco, store in db_active_dict.items():
                if db_ceco not in excel_dict:
                    store.status = 2
                    store.updated_at = current_time
                    stats_status_2 += 1
                    logger.info(f"tienda cambiada a status 2 - ceco: {store.ceco} | nombre: {store.name}")

            try:
                db.commit()
            except Exception as e:
                db.rollback()
                logger.error(f"error al commitear transaccion de sincronizacion: {e}")
                raise

            # imprimir metricas
            msg = (
                f"\n=== resultados de sincronizacion ===\n"
                f"1-> se encontraron en json y consulta (actualizados): {stats_updated_active}\n"
                f"2-> se encontraron en json pero no en consulta (insertados/restaurados): {stats_inserted_or_restored}\n"
                f"3-> se encontraron en consulta pero no en json (cambiado status a 2): {stats_status_2}\n"
                f"===================================="
            )
            print(msg)
            logger.info(msg)
