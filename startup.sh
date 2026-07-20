#!/bin/bash
# Script de arranque para Azure App Service (Linux)

# Arrancar FastAPI con Uvicorn (que ya lanza el bot por el evento startup de main.py)
# Azure por defecto inyecta la variable $PORT (usualmente 8000), pero uvicorn lo tomará
python run.py
