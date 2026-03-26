from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

# engine de conexion
engine = create_engine(settings.SQLALCHEMY_DATABASE_URI)

# fabrica de sesiones para inyeccion de dependencias
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# clase base para los modelos
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
