from sqlalchemy import Column, String, Integer, DateTime, BigInteger, UniqueConstraint
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class ConsolidatedFlow(Base):
    __tablename__ = "consolidated_flows"

    id = Column(BigInteger, primary_key=True, index=True)
    ip_src = Column(String, nullable=False)
    ip_dst = Column(String, nullable=False)
    port_dst = Column(Integer, nullable=False)
    protocol = Column(String(10), nullable=False)

    first_seen = Column(DateTime(timezone=True), nullable=False)
    last_seen = Column(DateTime(timezone=True), nullable=False)
    total_count = Column(BigInteger, default=1)

    __table_args__ = (
        UniqueConstraint('ip_src', 'ip_dst', 'port_dst', 'protocol', name='uq_flow_key'),
    )
