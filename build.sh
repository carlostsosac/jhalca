#!/usr/bin/env bash
# exit on error
set -o errexit

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el script para crear/actualizar las tablas de la base de datos
echo "Inicializando la base de datos..."
python init_db.py
echo "Inicialización de la base de datos completada."