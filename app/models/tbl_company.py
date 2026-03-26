from sqlalchemy import Column, String, BigInteger, DateTime, text
from sqlalchemy.orm import relationship
from app.core.database import Base

class TblCompany(Base):
    __tablename__ = "tbl_company"
    __table_args__ = {"schema": "sch_cctv"}

    id = Column(BigInteger, primary_key=True, server_default=text("nextval('sch_cctv.companies_id_seq1'::regclass)"))
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    delete_at = Column(DateTime(timezone=True), nullable=True)

    # relacion inversa con las tiendas
    stores = relationship("TblStore", back_populates="company")
