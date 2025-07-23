# -*- coding: utf-8 -*-
"""
Created on Tue Jun 17 16:00:54 2025

@author: cleit
"""

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from urllib.parse import quote_plus
import os
from dotenv import load_dotenv

# Carregar variáveis do .env
load_dotenv()

                # BANCO DE DADOS #

# Obter senha do .env
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = quote_plus(os.getenv("DB_PASSWORD"))
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")

DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"


engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Modelo do banco de dados
class PartDB(Base):
    __tablename__ = "almoxarifado"
    id = Column(Integer, primary_key=True, index=True)
    part_name = Column(String(100), index=True)
    manufacturer = Column(String(100), index=True)
    application_sector = Column(String(100), index=True)
    aircraft = Column(String(100), index=True)
    quantity = Column(Integer)
    value = Column(Float)

# Criar a tabela
Base.metadata.create_all(bind=engine)

                 # FASTAPI BACKEND #

# Schemas Pydantic
class Part(BaseModel):
    part_name: str
    manufacturer: str
    application_sector: str
    aircraft: str
    quantity: int
    value: float

class PartResponse(Part):
    id: int
    class Config:
        orm_mode = True

# App
app = FastAPI()

# Dependência de sessão
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Rotas
@app.post("/almoxarifado", response_model=PartResponse)
def create_part(part: Part, db: Session = Depends(get_db)):
    db_part = PartDB(**part.dict())
    db.add(db_part)
    try:
        db.commit()
        db.refresh(db_part)
        return db_part
    except:
        db.rollback()
        raise HTTPException(status_code=400, detail="Erro ao cadastrar peça.")

@app.get("/almoxarifado", response_model=List[PartResponse])
def list_parts(db: Session = Depends(get_db)):
    return db.query(PartDB).all()

@app.get("/almoxarifado/{part_id}", response_model=PartResponse)
def get_part(part_id: int, db: Session = Depends(get_db)):
    part = db.query(PartDB).filter(PartDB.id == part_id).first()
    if not part:
        raise HTTPException(status_code=404, detail="Peça não encontrada.")
    return part

