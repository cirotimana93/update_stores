import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging

logger = logging.getLogger(__name__)

class HttpClient:
    def __init__(self, headers: dict):
        self.session = requests.Session()
        self.session.headers.update(headers)
        
        # Configurar reintentos automaticos
        retry_strategy = Retry(
            total=3,  # Numero maximo de reintentos
            status_forcelist=[429, 500, 502, 503, 504],  # Codigos HTTP donde se reintentara
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"],  # Permitir reintentos tambien en POST
            backoff_factor=2  # Tiempo de espera (2s, 4s, 8s)
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)
        
    def post(self, url: str, data: dict = None, allow_redirects: bool = False):
        try:
            logger.info(f"realizando peticion post a {url}")
            response = self.session.post(url, data=data, allow_redirects=allow_redirects)
            
            # la respuesta 302 es esperada y correcta (Found)
            if response.status_code not in (200, 201, 302):
                response.raise_for_status()
                
            return response
        except requests.RequestException as e:
            logger.error(f"error realizando post a {url}: {e}")
            raise

    def get(self, url: str):
        try:
            logger.info(f"realizando peticion get a {url}")
            response = self.session.get(url)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            logger.error(f"error realizando get a {url}: {e}")
            raise
