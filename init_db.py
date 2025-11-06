from app import app
from models import db, Empresa, User, Role, Permission
from sqlalchemy import text, inspect

if __name__ == "__main__":
    with app.app_context():
        try:
            print("Creando todas las tablas definidas en los modelos...")
            db.create_all()
            print("¡Tablas creadas/verificadas con éxito!")

            inspector = inspect(db.engine)

            # Sembrar datos iniciales en la tabla de secuencias
            if inspector.has_table('secuencias'):
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
                    # Usar INSERT IGNORE para MySQL para evitar errores en 'clase' duplicada
                    db.session.execute(text("INSERT IGNORE INTO secuencias (codigo, secuencia, clase) VALUES (:codigo, :secuencia, :clase);"), s)
                db.session.commit()
                print("Datos de secuencias sembrados correctamente.")

            # Sembrar datos iniciales en la tabla 'empresa' si está vacía
            if inspector.has_table('empresa'):
                if db.session.query(Empresa).count() == 0:
                    print("La tabla 'empresa' está vacía. Creando registro inicial...")
                    db.session.add(Empresa(id=1, nombrec='Nombre de tu Empresa'))
                    db.session.commit()
                    print("Registro inicial de empresa creado.")

            # Sembrar roles iniciales si no existen
            if inspector.has_table('roles'):
                print("Verificando roles iniciales...")
                roles_a_crear = {
                    'admin': 'Administrador del sistema con todos los permisos.',
                    'user': 'Usuario estándar con permisos limitados.'
                }
                for role_name, role_desc in roles_a_crear.items():
                    if not Role.query.filter_by(name=role_name).first():
                        nuevo_rol = Role(name=role_name, description=role_desc)
                        db.session.add(nuevo_rol)
                        print(f"Rol '{role_name}' creado.")
                db.session.commit()
            
            # Sembrar permisos iniciales si no existen
            if inspector.has_table('permissions'):
                print("Verificando permisos iniciales...")
                permisos_a_crear = {
                    'acceso_usuarios': 'Acceso al formulario de Usuarios',
                    'acceso_roles': 'Acceso al formulario de Roles',
                    'acceso_clientes': 'Acceso al formulario de Clientes',
                    'acceso_proveedores': 'Acceso al formulario de Proveedores',
                    'acceso_mercancias': 'Acceso al formulario de Mercancías',
                    'acceso_tipos': 'Acceso al formulario de Tipos',
                    'acceso_facturas': 'Acceso al formulario de Facturas',
                    'acceso_compras': 'Acceso al formulario de Compras',
                    'acceso_cobros': 'Acceso al formulario de Cobros',
                    'acceso_pagos': 'Acceso al formulario de Pagos',
                    'acceso_devoluciones': 'Acceso al formulario de Devoluciones',
                    'acceso_ajustes_inv': 'Acceso al formulario de Ajustes de Inventario',
                    'acceso_gastos': 'Acceso al formulario de Gastos',
                    'acceso_empresa': 'Acceso al formulario de Datos de Empresa',
                    'acceso_reportes_ventas': 'Permite ver los reportes de ventas',
                }
                for perm_name, perm_desc in permisos_a_crear.items():
                    if not Permission.query.filter_by(name=perm_name).first():
                        db.session.add(Permission(name=perm_name, description=perm_desc))
                        print(f"Permiso '{perm_name}' creado.")
                db.session.commit()

            # Asignar todos los roles al usuario con ID 1
            if inspector.has_table('users') and inspector.has_table('roles'):
                user_1 = db.session.get(User, 1)
                if user_1:
                    print("Asignando todos los roles al usuario con ID 1...")
                    all_roles = Role.query.all()
                    if all_roles:
                        user_1.roles = all_roles
                        db.session.commit()
                        print(f"Se asignaron {len(all_roles)} roles a '{user_1.username}'.")
                    else:
                        print("No se encontraron roles para asignar.")
                else:
                    print("Usuario con ID 1 no encontrado. No se asignaron roles.")

        except Exception as e:
            db.session.rollback()
            print(f"Error durante la inicialización de la base de datos: {e}")