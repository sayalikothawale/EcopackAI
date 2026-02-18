import os

class Config:
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:password@localhost/ecopack_db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
