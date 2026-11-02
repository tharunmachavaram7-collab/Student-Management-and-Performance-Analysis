"""Configuration settings for the Student Performance Analysis System."""

import os
from dotenv import load_dotenv
load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-change-me')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///student_performance.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    VIP_ACCESS_KEY = os.environ.get('VIP_ACCESS_KEY', 'VIP')
    ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'VIP420')

