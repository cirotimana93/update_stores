import os
from pydantic import field_validator
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Config(BaseSettings):
    # por defecto asumiremos que esta en modo development si no se le pasa
    DEBUG: bool = True

    @field_validator("DEBUG", mode="before")
    @classmethod
    def parse_debug(cls, v):
        # si el valor en .env es el string "development", lo retorna como true
        if isinstance(v, str):
            return v.lower() == "development"
        return bool(v)

    # Credenciales Base de Datos
    DB_HOST_DTS_AWS: str = os.getenv("DB_HOST_DTS_AWS", "")
    DB_PORT_DTS_AWS: str = os.getenv("DB_PORT_DTS_AWS", "5432")
    DB_USER_DTS_AWS: str = os.getenv("DB_USER_DTS_AWS", "")
    DB_PASS_DTS_AWS: str = os.getenv("DB_PASS_DTS_AWS", "")
    DB_NAME_DTS_AWS: str = os.getenv("DB_NAME_DTS_AWS", "")

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        return f"postgresql://{self.DB_USER_DTS_AWS}:{self.DB_PASS_DTS_AWS}@{self.DB_HOST_DTS_AWS}:{self.DB_PORT_DTS_AWS}/{self.DB_NAME_DTS_AWS}"

    # urls para los reportes
    base_url: str = "https://gestion.apuestatotal.com"
    fastreport_cajas_url: str = f"{base_url}/fastreport/cajas/"
    
    # el excel se descarga desde aqui 
    export_files_base_url: str = f"{base_url}/export/files_export/cajas/"
    
    # headers utilizados en la peticion original
    headers: dict = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Accept-Language": "es-ES,es;q=0.9",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1"
    }

settings = Config()
