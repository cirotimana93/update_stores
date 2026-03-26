from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, text
from sqlalchemy.orm import relationship
from app.core.database import Base

class TblStore(Base):
    __tablename__ = "tbl_store"
    __table_args__ = {"schema": "sch_cctv"}

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('sch_cctv.stores_id_seq1'::regclass)"))
    name = Column(String, nullable=False)
    ceco = Column(String, nullable=False)
    supervisor = Column(String, nullable=True)
    company_id = Column(Integer, ForeignKey("sch_cctv.tbl_company.id"), nullable=False)
    status = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    delete_at = Column(DateTime(timezone=True), nullable=True)

    # relacion con la empresa (tabla principal)
    company = relationship("TblCompany", back_populates="stores")
