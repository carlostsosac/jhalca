-- SQL script para crear las tablas en una base de datos PostgreSQL.
-- Este script es una adaptación del original para MySQL.

-- Tabla de usuarios
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    fullname VARCHAR(255),
    photo_url VARCHAR(500)
);

-- Tabla de roles
CREATE TABLE roles (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) UNIQUE,
    description VARCHAR(255)
);

-- Tabla de permisos
CREATE TABLE permissions (
    id SERIAL PRIMARY KEY,
    name VARCHAR(150) UNIQUE,
    description VARCHAR(255)
);

-- Tabla de asociación usuario-rol
CREATE TABLE user_roles (
    user_id INT,
    role_id INT,
    PRIMARY KEY (user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

-- Tabla de asociación rol-permiso
CREATE TABLE role_permissions (
    role_id INT,
    permission_id INT,
    PRIMARY KEY (role_id, permission_id),
    FOREIGN KEY (role_id) REFERENCES roles(id),
    FOREIGN KEY (permission_id) REFERENCES permissions(id)
);

-- Tabla de la empresa
CREATE TABLE empresa (
    id SERIAL PRIMARY KEY,
    nombrec VARCHAR(255) NOT NULL,
    direccionc VARCHAR(500),
    telefonos VARCHAR(100),
    correo VARCHAR(100),
    rnc VARCHAR(50),
    logo VARCHAR(255)
);

-- Tabla de clientes
CREATE TABLE clientes (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255),
    rnc VARCHAR(50),
    contacto VARCHAR(255),
    telefono VARCHAR(100),
    direccion VARCHAR(255),
    correo VARCHAR(255)
);

-- Tabla de proveedores
CREATE TABLE proveedores (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(255),
    rnc VARCHAR(50),
    contacto VARCHAR(255),
    telefono VARCHAR(100),
    direccion VARCHAR(255),
    correo VARCHAR(255)
);

-- Tabla de tipos (categorías)
CREATE TABLE tipos (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    clase VARCHAR(50) NOT NULL
);

-- Tabla de mercancías
CREATE TABLE mercancias (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    nombre VARCHAR(255),
    precio DECIMAL(10, 2),
    existencia INT DEFAULT 0,
    costo DECIMAL(10, 2),
    tipo VARCHAR(50),
    clase_id INT NULL,
    FOREIGN KEY (clase_id) REFERENCES tipos(id)
);

-- Encabezado de ajustes de inventario
CREATE TABLE ajustec (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    fecha DATE,
    clase VARCHAR(50),
    comentario VARCHAR(255),
    total DECIMAL(10, 2),
    estado VARCHAR(20) DEFAULT 'activo'
);

-- Detalle de ajustes de inventario
CREATE TABLE ajusted (
    id SERIAL PRIMARY KEY,
    ajuste_id INT,
    mercancia_id INT,
    cantidad INT,
    costo DECIMAL(10, 2),
    FOREIGN KEY (ajuste_id) REFERENCES ajustec(id),
    FOREIGN KEY (mercancia_id) REFERENCES mercancias(id)
);

-- Tabla de gastos
CREATE TABLE gastos (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    fecha DATE,
    descripcion VARCHAR(255),
    monto DECIMAL(10, 2),
    documento VARCHAR(255),
    clase_id INT,
    FOREIGN KEY (clase_id) REFERENCES tipos(id)
);

-- Encabezado de facturas
CREATE TABLE facturasc (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    fecha DATE,
    referencia VARCHAR(50),
    condicion VARCHAR(50),
    cliente_id INT NULL,
    comentario VARCHAR(255),
    estado VARCHAR(20) NOT NULL DEFAULT 'cotizado',
    subtotal DECIMAL(10,2) NULL,
    itbis DECIMAL(10,2) NULL,
    descuento DECIMAL(10,2) NULL,
    total DECIMAL(10,2) NULL,
    balance DECIMAL(10,2) NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

-- Detalle de facturas
CREATE TABLE facturasd (
    id SERIAL PRIMARY KEY,
    factura_id INT NOT NULL,
    mercancia_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio DECIMAL(10,2) NULL,
    costo DECIMAL(10,2) NULL,
    importe DECIMAL(10,2) NULL,
    FOREIGN KEY (factura_id) REFERENCES facturasc(id),
    FOREIGN KEY (mercancia_id) REFERENCES mercancias(id)
);

-- Encabezado de compras
CREATE TABLE comprasc (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    fecha DATE,
    referencia VARCHAR(50),
    condicion VARCHAR(50),
    proveedor_id INT NULL,
    comentario VARCHAR(255),
    estado VARCHAR(20) NOT NULL DEFAULT 'facturado',
    subtotal DECIMAL(10,2) NULL,
    itbis DECIMAL(10,2) NULL,
    descuento DECIMAL(10,2) NULL,
    total DECIMAL(10,2) NULL,
    balance DECIMAL(10,2) NULL,
    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
);

-- Detalle de compras
CREATE TABLE comprasd (
    id SERIAL PRIMARY KEY,
    compra_id INT NOT NULL,
    mercancia_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio DECIMAL(10,2) NULL,
    costo DECIMAL(10,2) NULL,
    importe DECIMAL(10,2) NULL,
    FOREIGN KEY (compra_id) REFERENCES comprasc(id),
    FOREIGN KEY (mercancia_id) REFERENCES mercancias(id)
);

-- Encabezado de cobros
CREATE TABLE cobrosc (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    fecha DATE,
    cliente_id INT,
    estado VARCHAR(20) NOT NULL DEFAULT 'activo',
    comentario VARCHAR(255),
    forma_pago VARCHAR(50),
    descuentos DECIMAL(10,2) NULL,
    cargos DECIMAL(10,2) NULL,
    total DECIMAL(10,2) NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

-- Detalle de cobros
CREATE TABLE cobrosd (
    id SERIAL PRIMARY KEY,
    cobro_id INT NOT NULL,
    factura_id INT NOT NULL,
    aplicado DECIMAL(10,2) NULL,
    descuento DECIMAL(10,2) NULL,
    cargo DECIMAL(10,2) NULL,
    FOREIGN KEY (cobro_id) REFERENCES cobrosc(id),
    FOREIGN KEY (factura_id) REFERENCES facturasc(id)
);

-- Encabezado de pagos
CREATE TABLE pagosc (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    fecha DATE,
    proveedor_id INT,
    estado VARCHAR(20) NOT NULL DEFAULT 'activo',
    comentario VARCHAR(255),
    forma_pago VARCHAR(50),
    descuentos DECIMAL(10,2) NULL,
    cargos DECIMAL(10,2) NULL,
    total DECIMAL(10,2) NULL,
    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
);

-- Detalle de pagos
CREATE TABLE pagosd (
    id SERIAL PRIMARY KEY,
    pago_id INT NOT NULL,
    compra_id INT NOT NULL,
    aplicado DECIMAL(10,2) NULL,
    descuento DECIMAL(10,2) NULL,
    cargo DECIMAL(10,2) NULL,
    FOREIGN KEY (pago_id) REFERENCES pagosc(id),
    FOREIGN KEY (compra_id) REFERENCES comprasc(id)
);

-- Encabezado de devoluciones
CREATE TABLE devolucionc (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    fecha DATE,
    tipo VARCHAR(20) NOT NULL,
    cliente_id INT NULL,
    proveedor_id INT NULL,
    comentario VARCHAR(255),
    estado VARCHAR(20) NOT NULL DEFAULT 'activa',
    subtotal DECIMAL(10,2) NULL,
    itbis DECIMAL(10,2) NULL,
    total DECIMAL(10,2) NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
);

-- Detalle de devoluciones
CREATE TABLE devoluciond (
    id SERIAL PRIMARY KEY,
    devolucion_id INT NOT NULL,
    mercancia_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio DECIMAL(10,2) NULL,
    importe DECIMAL(10,2) NULL,
    factura_id INT NULL,
    compra_id INT NULL,
    FOREIGN KEY (devolucion_id) REFERENCES devolucionc(id),
    FOREIGN KEY (mercancia_id) REFERENCES mercancias(id),
    FOREIGN KEY (factura_id) REFERENCES facturasc(id),
    FOREIGN KEY (compra_id) REFERENCES comprasc(id)
);

-- Tabla de secuencias para códigos automáticos
CREATE TABLE secuencias (
    id SERIAL PRIMARY KEY,
    codigo VARCHAR(20) NULL,
    secuencia INT NOT NULL DEFAULT 1,
    clase VARCHAR(50) NOT NULL UNIQUE
);

-- Insertar secuencias iniciales (si no existen)
INSERT INTO secuencias (codigo, secuencia, clase) VALUES ('F', 1, 'factura') ON CONFLICT (clase) DO NOTHING;
INSERT INTO secuencias (codigo, secuencia, clase) VALUES ('CM', 1, 'compra') ON CONFLICT (clase) DO NOTHING;
INSERT INTO secuencias (codigo, secuencia, clase) VALUES ('RC', 1, 'cobro') ON CONFLICT (clase) DO NOTHING;
INSERT INTO secuencias (codigo, secuencia, clase) VALUES ('PA', 1, 'pago') ON CONFLICT (clase) DO NOTHING;
INSERT INTO secuencias (codigo, secuencia, clase) VALUES ('AJ', 1, 'ajuste') ON CONFLICT (clase) DO NOTHING;
INSERT INTO secuencias (codigo, secuencia, clase) VALUES ('DV', 1, 'devolucion_venta') ON CONFLICT (clase) DO NOTHING;
INSERT INTO secuencias (codigo, secuencia, clase) VALUES ('DC', 1, 'devolucion_compra') ON CONFLICT (clase) DO NOTHING;
INSERT INTO secuencias (codigo, secuencia, clase) VALUES ('G', 1, 'gasto') ON CONFLICT (clase) DO NOTHING;

-- Insertar registro inicial para la empresa (si no existe)
INSERT INTO empresa (id, nombrec) VALUES (1, 'Nombre de tu Empresa') ON CONFLICT (id) DO NOTHING;

-- Insertar usuario administrador inicial
INSERT INTO users (username, password_hash, fullname) VALUES ('admin', '12', 'Carlos sosa') ON CONFLICT (username) DO NOTHING;