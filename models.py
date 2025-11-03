from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# Association tables
user_roles = db.Table('user_roles',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id'))
)

role_permissions = db.Table('role_permissions',
    db.Column('role_id', db.Integer, db.ForeignKey('roles.id')),
    db.Column('permission_id', db.Integer, db.ForeignKey('permissions.id'))
)

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    fullname = db.Column(db.String(255))
    photo_url = db.Column(db.String(500))
    roles = db.relationship('Role', secondary=user_roles, backref='users')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        if not self.password_hash:
            return False
        # Detecta hashes generados por Werkzeug (pbkdf2/scrypt/argon2). Si no, compara texto plano.
        if self.password_hash.startswith(('pbkdf2:', 'scrypt:', 'argon2:')):
            return check_password_hash(self.password_hash, password)
        return self.password_hash == password

    @staticmethod
    def authenticate(username, password):
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            return user
        return None

    def has_role(self, role_name):
        return any(r.name == role_name for r in self.roles)
    
    def has_permission(self, perm_name):
        if self.has_role('admin'):
            return True
        for r in self.roles:
            for p in r.permissions:
                if p.name == perm_name:
                    return True
        return False

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    description = db.Column(db.String(255))
    permissions = db.relationship('Permission', secondary=role_permissions, backref='roles')

class Permission(db.Model):
    __tablename__ = 'permissions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    description = db.Column(db.String(255))

class Empresa(db.Model):
    __tablename__ = 'empresa'
    id = db.Column(db.Integer, primary_key=True) # Código
    nombrec = db.Column(db.String(255), nullable=False, default='Mi Empresa')
    direccionc = db.Column(db.String(500))
    telefonos = db.Column(db.String(100))
    correo = db.Column(db.String(100))
    rnc = db.Column(db.String(50))
    logo = db.Column(db.String(255)) # Ruta al archivo del logo

    def __repr__(self):
        return f'<Empresa {self.nombrec}>'

# Example business tables (scaffold)
class Cliente(db.Model):
    __tablename__ = 'clientes'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255))
    rnc = db.Column(db.String(50))
    contacto = db.Column(db.String(255))
    telefono = db.Column(db.String(100))
    direccion = db.Column(db.String(255))
    correo = db.Column(db.String(255))

class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255))
    rnc = db.Column(db.String(50))
    contacto = db.Column(db.String(255))
    telefono = db.Column(db.String(100))
    direccion = db.Column(db.String(255))
    correo = db.Column(db.String(255))

class Tipo(db.Model):
    __tablename__ = 'tipos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    clase = db.Column(db.String(50), nullable=False)  # ej: 'mercancia', 'cliente', 'proveedor'
    
    def __repr__(self):
        return f'<Tipo {self.nombre} ({self.clase})>'

class Mercancia(db.Model):
    __tablename__ = 'mercancias'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True)
    nombre = db.Column(db.String(255))
    precio = db.Column(db.Numeric(10, 2))
    existencia = db.Column(db.Integer, default=0)
    costo = db.Column(db.Numeric(10, 2))
    tipo = db.Column(db.String(50))
    clase_id = db.Column(db.Integer, db.ForeignKey('tipos.id'))
    
    # Relación con la tabla tipos
    clase = db.relationship('Tipo', backref='mercancias')

class Gasto(db.Model):
    __tablename__ = 'gastos'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True)
    fecha = db.Column(db.Date)
    descripcion = db.Column(db.String(255))
    monto = db.Column(db.Numeric(10, 2))
    documento = db.Column(db.String(255))
    clase_id = db.Column(db.Integer, db.ForeignKey('tipos.id'))
    clase = db.relationship('Tipo', backref='gastos')

# === AJUSTES INVENARIO ===
class AjusteC(db.Model):
    __tablename__ = 'ajustec'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True)
    fecha = db.Column(db.Date)
    clase = db.Column(db.String(50))
    comentario = db.Column(db.String(255))
    total = db.Column(db.Numeric(10, 2))
    estado = db.Column(db.String(20), default='activo')  # activo, cancelado

    detalles = db.relationship('AjusteD', backref='ajuste', cascade='all, delete-orphan')

class AjusteD(db.Model):
    __tablename__ = 'ajusted'
    id = db.Column(db.Integer, primary_key=True)
    ajuste_id = db.Column(db.Integer, db.ForeignKey('ajustec.id'))
    mercancia_id = db.Column(db.Integer, db.ForeignKey('mercancias.id'))
    cantidad = db.Column(db.Integer)
    costo = db.Column(db.Numeric(10, 2))

    mercancia = db.relationship('Mercancia')

# === FACTURAS ===
class FacturaC(db.Model):
    __tablename__ = 'facturasc'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True)
    fecha = db.Column(db.Date)
    referencia = db.Column(db.String(50))
    condicion = db.Column(db.String(50))
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    comentario = db.Column(db.String(255))
    estado = db.Column(db.String(20), default='cotizado')  # cotizado, facturado
    subtotal = db.Column(db.Numeric(10, 2))
    itbis = db.Column(db.Numeric(10, 2))
    descuento = db.Column(db.Numeric(10, 2))
    total = db.Column(db.Numeric(10, 2))
    balance = db.Column(db.Numeric(10, 2))

    cliente = db.relationship('Cliente')
    detalles = db.relationship('FacturaD', backref='factura', cascade='all, delete-orphan')

class FacturaD(db.Model):
    __tablename__ = 'facturasd'
    id = db.Column(db.Integer, primary_key=True)
    factura_id = db.Column(db.Integer, db.ForeignKey('facturasc.id'))
    mercancia_id = db.Column(db.Integer, db.ForeignKey('mercancias.id'))
    cantidad = db.Column(db.Integer)
    precio = db.Column(db.Numeric(10, 2))
    costo = db.Column(db.Numeric(10, 2))
    importe = db.Column(db.Numeric(10, 2))

    mercancia = db.relationship('Mercancia')

# === COMPRAS ===
class ComprasC(db.Model):
    __tablename__ = 'comprasc'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True)
    fecha = db.Column(db.Date)
    referencia = db.Column(db.String(50))
    condicion = db.Column(db.String(50))
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'))
    comentario = db.Column(db.String(255))
    estado = db.Column(db.String(20), default='cotizado')  # cotizado, facturado
    subtotal = db.Column(db.Numeric(10, 2))
    itbis = db.Column(db.Numeric(10, 2))
    descuento = db.Column(db.Numeric(10, 2))
    total = db.Column(db.Numeric(10, 2))
    balance = db.Column(db.Numeric(10, 2))

    proveedor = db.relationship('Proveedor')
    detalles = db.relationship('ComprasD', backref='compra', cascade='all, delete-orphan')

class ComprasD(db.Model):
    __tablename__ = 'comprasd'
    id = db.Column(db.Integer, primary_key=True)
    compra_id = db.Column(db.Integer, db.ForeignKey('comprasc.id'))
    mercancia_id = db.Column(db.Integer, db.ForeignKey('mercancias.id'))
    cantidad = db.Column(db.Integer)
    precio = db.Column(db.Numeric(10, 2))
    costo = db.Column(db.Numeric(10, 2))
    importe = db.Column(db.Numeric(10, 2))

    mercancia = db.relationship('Mercancia')

# === COBROS (CUENTAS POR COBRAR) ===
class CobroC(db.Model):
    __tablename__ = 'cobrosc'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True)
    fecha = db.Column(db.Date)
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'))
    estado = db.Column(db.String(20), default='activo') # 'activo', 'cancelado'
    comentario = db.Column(db.String(255))
    forma_pago = db.Column(db.String(50))
    descuentos = db.Column(db.Numeric(10, 2))
    cargos = db.Column(db.Numeric(10, 2))
    total = db.Column(db.Numeric(10, 2))

    cliente = db.relationship('Cliente')
    detalles = db.relationship('CobroD', backref='cobro', cascade='all, delete-orphan')

class CobroD(db.Model):
    __tablename__ = 'cobrosd'
    id = db.Column(db.Integer, primary_key=True)
    cobro_id = db.Column(db.Integer, db.ForeignKey('cobrosc.id'))
    factura_id = db.Column(db.Integer, db.ForeignKey('facturasc.id'))
    aplicado = db.Column(db.Numeric(10, 2))
    descuento = db.Column(db.Numeric(10, 2))
    cargo = db.Column(db.Numeric(10, 2))

    factura = db.relationship('FacturaC')

# === PAGOS (CUENTAS POR PAGAR) ===
class PagoC(db.Model):
    __tablename__ = 'pagosc'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True)
    fecha = db.Column(db.Date)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'))
    estado = db.Column(db.String(20), default='activo') # 'activo', 'cancelado'
    comentario = db.Column(db.String(255))
    forma_pago = db.Column(db.String(50))
    descuentos = db.Column(db.Numeric(10, 2))
    cargos = db.Column(db.Numeric(10, 2))
    total = db.Column(db.Numeric(10, 2))

    proveedor = db.relationship('Proveedor')
    detalles = db.relationship('PagoD', backref='pago', cascade='all, delete-orphan')

class PagoD(db.Model):
    __tablename__ = 'pagosd'
    id = db.Column(db.Integer, primary_key=True)
    pago_id = db.Column(db.Integer, db.ForeignKey('pagosc.id'))
    compra_id = db.Column(db.Integer, db.ForeignKey('comprasc.id'))
    aplicado = db.Column(db.Numeric(10, 2))
    descuento = db.Column(db.Numeric(10, 2))
    cargo = db.Column(db.Numeric(10, 2))

    compra = db.relationship('ComprasC')

# === DEVOLUCIONES (SOBRE COMPRAS Y VENTAS) ===
class DevolucionC(db.Model):
    __tablename__ = 'devolucionc'
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), unique=True)
    fecha = db.Column(db.Date)
    tipo = db.Column(db.String(20)) # 'venta' o 'compra'
    
    cliente_id = db.Column(db.Integer, db.ForeignKey('clientes.id'), nullable=True)
    proveedor_id = db.Column(db.Integer, db.ForeignKey('proveedores.id'), nullable=True)
    
    comentario = db.Column(db.String(255))
    estado = db.Column(db.String(20), default='activa') # 'activa', 'cancelada'
    
    subtotal = db.Column(db.Numeric(10, 2))
    itbis = db.Column(db.Numeric(10, 2))
    total = db.Column(db.Numeric(10, 2))

    cliente = db.relationship('Cliente')
    proveedor = db.relationship('Proveedor')
    detalles = db.relationship('DevolucionD', backref='devolucion', cascade='all, delete-orphan')

class DevolucionD(db.Model):
    __tablename__ = 'devoluciond'
    id = db.Column(db.Integer, primary_key=True)
    devolucion_id = db.Column(db.Integer, db.ForeignKey('devolucionc.id'))
    mercancia_id = db.Column(db.Integer, db.ForeignKey('mercancias.id'))
    
    # Referencia al documento original
    factura_id = db.Column(db.Integer, db.ForeignKey('facturasc.id'), nullable=True)
    compra_id = db.Column(db.Integer, db.ForeignKey('comprasc.id'), nullable=True)

    cantidad = db.Column(db.Integer)
    precio = db.Column(db.Numeric(10, 2)) # Precio/Costo al que se devuelve
    importe = db.Column(db.Numeric(10, 2))

    mercancia = db.relationship('Mercancia')
    factura = db.relationship('FacturaC')
    compra = db.relationship('ComprasC')
