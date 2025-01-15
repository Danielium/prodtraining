from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
from sqlalchemy import create_engine, Column, String, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from typing import List, Optional
from pydantic import BaseModel
import os

app = FastAPI()

# Подключение к БД
DATABASE_URL = os.getenv("POSTGRES_CONN", "postgresql://postgres:postgres@localhost:5432/postgres")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Модель SQLAlchemy для работы с БД
class CountryDB(Base):
    __tablename__ = "countries"
    name = Column(String)
    alpha2 = Column(String, primary_key=True)
    alpha3 = Column(String)
    region = Column(String)

@app.get("/api/countries")
async def get_countries(
    region: Optional[List[str]] = Query(None, description="Возвращаемые страны должны относиться только к тем регионам, которые переданы в данном списке.")
):
    db = SessionLocal()
    try:
        query = select(CountryDB)
        
        if region:
            # Проверяем корректность всех регионов
            existing_regions = db.execute(select(CountryDB.region).distinct()).scalars().all()
            if not all(r in existing_regions for r in region):
                return JSONResponse(
                    status_code=400,
                    content={"message": "Invalid region provided"}
                )
            query = query.where(CountryDB.region.in_(region))
        
        # Сортировка по alpha2
        query = query.order_by(CountryDB.alpha2)
        countries = db.execute(query).scalars().all()
        
        return [
            {
                "name": country.name,
                "alpha2": country.alpha2,
                "alpha3": country.alpha3,
                "region": country.region
            }
            for country in countries
        ]
    finally:
        db.close()

@app.get("/api/countries/{alpha2}")
async def get_country_by_alpha2(alpha2: str):
    if not alpha2.isalpha() or len(alpha2) != 2:
        return JSONResponse(
            status_code=400,
            content={"message": "Invalid alpha2 format"}
        )
    
    db = SessionLocal()
    try:
        country = db.execute(
            select(CountryDB).where(CountryDB.alpha2 == alpha2.upper())
        ).scalar_one_or_none()
        
        if not country:
            return JSONResponse(
                status_code=404,
                content={"message": "Country not found"}
            )
            
        return {
            "name": country.name,
            "alpha2": country.alpha2,
            "alpha3": country.alpha3,
            "region": country.region
        }
    finally:
        db.close()
