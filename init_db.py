from app import app
from models import db, Empresa
from sqlalchemy import text, inspect
from sqlalchemy.exc import IntegrityError

if __name__ == "__main__":
    with app.app_context():
        try:
            print("Creando todas las tablas definidas en los modelos...")
            db.create_all()
            print("¡Tablas creadas/verificadas con éxito!")

            # Sembrar datos iniciales en la tabla de secuencias
            print("Sembrando datos iniciales en la tabla 'secuencias'...")
            secuencias_iniciales = [
                {'codigo': 'F', 'secuencia': 1, 'clase': 'factura'},
                {'codigo': 'CM', 'secuencia': 1, 'clase': 'compra'},
                {'codigo': 'RC', 'secuencia': 1, 'clase': 'cobro'},
                {'codigo': 'PA', 'secuencia': 1, 'clase': 'pago'},
                {'codigo': 'AJ', 'secuencia': 1, 'clase': 'ajuste'},
                {'codigo': 'DV', 'secuencia': 1, 'clase': 'devolucion_venta'},
                {'codigo': 'DC', 'secuencia': 1, 'clase': 'devolucion_compra'},
                {'codigo': 'G', 'secuencia': 1, 'clase': 'gasto'}
            ]
            for s in secuencias_iniciales:
                db.session.execute(text("INSERT INTO secuencias (codigo, secuencia, clase) VALUES (:codigo, :secuencia, :clase) ON DUPLICATE KEY UPDATE clase=clase;"), s)
            db.session.commit()
            print("Datos de secuencias sembrados correctamente.")

            # Sembrar datos iniciales en la tabla 'empresa' si está vacía
            inspector = inspect(db.engine)
            if inspector.has_table('empresa'):
                if db.session.query(Empresa).count() == 0:
                    print("La tabla 'empresa' está vacía. Creando registro inicial...")
                    db.session.add(Empresa(id=1, nombrec='Nombre de tu Empresa'))
                    db.session.commit()
                    print("Registro inicial de empresa creado.")

        except Exception as e:
            print(f"Error durante la inicialización de la base de datos: {e}")