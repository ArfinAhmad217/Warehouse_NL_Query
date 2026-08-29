from sqlalchemy import create_engine, text, Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime, timedelta
import random
import os
from app.config import settings

os.makedirs("data", exist_ok=True)

engine = create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ====================== SCHEMA ======================
class Chamber(Base):
    __tablename__ = "chambers"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)          # e.g. CH-01, CH-02
    location = Column(String(100))
    total_capacity_cbm = Column(Float)              # cubic meter
    is_active = Column(Boolean, default=True)

class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True)
    sku = Column(String(50), unique=True)
    name = Column(String(100))
    category = Column(String(50))
    volume_cbm = Column(Float)                      # per unit volume

class InventorySnapshot(Base):
    __tablename__ = "inventory_snapshots"
    id = Column(Integer, primary_key=True)
    chamber_id = Column(Integer, ForeignKey("chambers.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer)
    snapshot_date = Column(DateTime)
    used_capacity_cbm = Column(Float)               # quantity * volume_cbm

    chamber = relationship("Chamber")
    product = relationship("Product")

class CapacityLog(Base):
    __tablename__ = "capacity_logs"
    id = Column(Integer, primary_key=True)
    chamber_id = Column(Integer, ForeignKey("chambers.id"))
    log_date = Column(DateTime)
    used_capacity_cbm = Column(Float)
    total_capacity_cbm = Column(Float)
    utilization_pct = Column(Float)                 # (used/total)*100

    chamber = relationship("Chamber")
    
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(100), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# ====================== INIT + SEED ======================
def init_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # already seeded?
    if db.query(Chamber).count() > 0:
        db.close()
        return

    # Chambers
    chambers = [
        Chamber(name="CH-01", location="Zone A", total_capacity_cbm=5000),
        Chamber(name="CH-02", location="Zone A", total_capacity_cbm=4500),
        Chamber(name="CH-03", location="Zone B", total_capacity_cbm=6000),
        Chamber(name="CH-04", location="Zone B", total_capacity_cbm=3800),
        Chamber(name="CH-05", location="Zone C", total_capacity_cbm=7200),
    ]
    db.add_all(chambers)
    db.commit()

    # Products
    products = [
        Product(sku="SKU-1001", name="Wheat Flour 50kg", category="Grain", volume_cbm=0.08),
        Product(sku="SKU-1002", name="Rice 25kg", category="Grain", volume_cbm=0.04),
        Product(sku="SKU-2001", name="Cooking Oil 15L", category="Oil", volume_cbm=0.02),
        Product(sku="SKU-3001", name="Sugar 50kg", category="Sweetener", volume_cbm=0.07),
        Product(sku="SKU-4001", name="Dal 30kg", category="Pulse", volume_cbm=0.05),
    ]
    db.add_all(products)
    db.commit()

    # Generate last 90 days capacity logs
    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    for day in range(90):
        log_date = today - timedelta(days=day)
        for ch in chambers:
            used = random.uniform(ch.total_capacity_cbm * 0.4, ch.total_capacity_cbm * 0.95)
            util = round((used / ch.total_capacity_cbm) * 100, 2)
            db.add(CapacityLog(
                chamber_id=ch.id,
                log_date=log_date,
                used_capacity_cbm=round(used, 2),
                total_capacity_cbm=ch.total_capacity_cbm,
                utilization_pct=util
            ))
    db.commit()
    db.close()
    print("✅ Database initialized + seeded with 90 days data")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()