-- SQL script scaffold to create minimal tables for the Flask app.
-- SQL script para crear las tablas en una base de datos MySQL.

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    fullname VARCHAR(255),
    photo_url VARCHAR(500)
);

CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) UNIQUE,
    description VARCHAR(255)
);

CREATE TABLE permissions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) UNIQUE,
    description VARCHAR(255)
);

CREATE TABLE user_roles (
    user_id INT,
    role_id INT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (role_id) REFERENCES roles(id)
);

CREATE TABLE role_permissions (
    role_id INT,
    permission_id INT,
    FOREIGN KEY (role_id) REFERENCES roles(id),
    FOREIGN KEY (permission_id) REFERENCES permissions(id)
);

CREATE TABLE empresa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombrec VARCHAR(255) NOT NULL,
    direccionc VARCHAR(500),
    telefonos VARCHAR(100),
    correo VARCHAR(100),
    rnc VARCHAR(50),
    logo VARCHAR(255)
);

CREATE TABLE clientes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255),
    rnc VARCHAR(50),
    contacto VARCHAR(255),
    telefono VARCHAR(100),
    direccion VARCHAR(255),
    correo VARCHAR(255)
);

CREATE TABLE proveedores (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(255),
    rnc VARCHAR(50),
    contacto VARCHAR(255),
    telefono VARCHAR(100),
    direccion VARCHAR(255),
    correo VARCHAR(255)
);

CREATE TABLE tipos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    clase VARCHAR(50) NOT NULL
);

CREATE TABLE mercancias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    nombre VARCHAR(255),
    precio DECIMAL(10, 2),
    existencia INT DEFAULT 0,
    costo DECIMAL(10, 2),
    tipo VARCHAR(50),
    clase_id INT NULL,
    FOREIGN KEY (clase_id) REFERENCES tipos(id)
);

CREATE TABLE ajustec (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    fecha DATE,
    clase VARCHAR(50),
    comentario VARCHAR(255),
    total DECIMAL(10, 2),
    estado VARCHAR(20) DEFAULT 'activo'
);

CREATE TABLE ajusted (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ajuste_id INT,
    mercancia_id INT,
    cantidad INT,
    costo DECIMAL(10, 2),
    FOREIGN KEY (ajuste_id) REFERENCES ajustec(id),
    FOREIGN KEY (mercancia_id) REFERENCES mercancias(id)
);

CREATE TABLE gastos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    fecha DATE
);

CREATE TABLE facturasc (
    id INT AUTO_INCREMENT PRIMARY KEY,
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

CREATE TABLE facturasd (
    id INT AUTO_INCREMENT PRIMARY KEY,
    factura_id INT NOT NULL,
    mercancia_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio DECIMAL(10,2) NULL,
    costo DECIMAL(10,2) NULL,
    importe DECIMAL(10,2) NULL,
    FOREIGN KEY (factura_id) REFERENCES facturasc(id),
    FOREIGN KEY (mercancia_id) REFERENCES mercancias(id)
);

CREATE TABLE comprasc (
    id INT AUTO_INCREMENT PRIMARY KEY,
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

CREATE TABLE comprasd (
    id INT AUTO_INCREMENT PRIMARY KEY,
    compra_id INT NOT NULL,
    mercancia_id INT NOT NULL,
    cantidad INT NOT NULL,
    precio DECIMAL(10,2) NULL,
    costo DECIMAL(10,2) NULL,
    importe DECIMAL(10,2) NULL,
    FOREIGN KEY (compra_id) REFERENCES comprasc(id),
    FOREIGN KEY (mercancia_id) REFERENCES mercancias(id)
);

CREATE TABLE cobrosc (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    fecha DATE,
    cliente_id INT,
    estado VARCHAR(20) NOT NULL DEFAULT 'activo', -- 'activo', 'cancelado'
    comentario VARCHAR(255),
    forma_pago VARCHAR(50),
    descuentos DECIMAL(10,2) NULL,
    cargos DECIMAL(10,2) NULL,
    total DECIMAL(10,2) NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id)
);

CREATE TABLE cobrosd (
    id INT AUTO_INCREMENT PRIMARY KEY,
    cobro_id INT NOT NULL,
    factura_id INT NOT NULL,
    aplicado DECIMAL(10,2) NULL,
    descuento DECIMAL(10,2) NULL,
    cargo DECIMAL(10,2) NULL,
    FOREIGN KEY (cobro_id) REFERENCES cobrosc(id),
    FOREIGN KEY (factura_id) REFERENCES facturasc(id)
);

CREATE TABLE pagosc (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    fecha DATE,
    proveedor_id INT,
    estado VARCHAR(20) NOT NULL DEFAULT 'activo', -- 'activo', 'cancelado'
    comentario VARCHAR(255),
    forma_pago VARCHAR(50),
    descuentos DECIMAL(10,2) NULL,
    cargos DECIMAL(10,2) NULL,
    total DECIMAL(10,2) NULL,
    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
);

CREATE TABLE pagosd (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pago_id INT NOT NULL,
    compra_id INT NOT NULL,
    aplicado DECIMAL(10,2) NULL,
    descuento DECIMAL(10,2) NULL,
    cargo DECIMAL(10,2) NULL,
    FOREIGN KEY (pago_id) REFERENCES pagosc(id),
    FOREIGN KEY (compra_id) REFERENCES comprasc(id)
);

CREATE TABLE devolucionc (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(50) UNIQUE,
    fecha DATE,
    tipo VARCHAR(20) NOT NULL, -- 'venta' o 'compra'
    cliente_id INT NULL,
    proveedor_id INT NULL,
    comentario VARCHAR(255),
    estado VARCHAR(20) NOT NULL DEFAULT 'activa', -- 'activa', 'cancelada'
    subtotal DECIMAL(10,2) NULL,
    itbis DECIMAL(10,2) NULL,
    total DECIMAL(10,2) NULL,
    FOREIGN KEY (cliente_id) REFERENCES clientes(id),
    FOREIGN KEY (proveedor_id) REFERENCES proveedores(id)
);

CREATE TABLE devoluciond (
    id INT AUTO_INCREMENT PRIMARY KEY,
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

CREATE TABLE secuencias (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo VARCHAR(20) NULL,
    secuencia INT NOT NULL DEFAULT 1,
    clase VARCHAR(50) NOT NULL UNIQUE
);

-- Insertar secuencias iniciales
INSERT INTO secuencias (codigo, secuencia, clase) VALUES ('F', 1, 'factura') ON DUPLICATE KEY UPDATE clase=clase;
INSERT INTO secuencias (codigo, secuencia, clase) VALUES ('CM', 1, 'compra') ON DUPLICATE KEY UPDATE clase=clase;
INSERT INTO secuencias (codigo, secuencia, clase) VALUES ('RC', 1, 'cobro') ON DUPLICATE KEY UPDATE clase=clase;
INSERT INTO secuencias (codigo, secuencia, clase) VALUES ('PA', 1, 'pago') ON DUPLICATE KEY UPDATE clase=clase;
INSERT INTO secuencias (codigo, secuencia, clase) VALUES ('AJ', 1, 'ajuste') ON DUPLICATE KEY UPDATE clase=clase;
INSERT INTO secuencias (codigo, secuencia, clase) VALUES ('DV', 1, 'devolucion_venta') ON DUPLICATE KEY UPDATE clase=clase;
INSERT INTO secuencias (codigo, secuencia, clase) VALUES ('DC', 1, 'devolucion_compra') ON DUPLICATE KEY UPDATE clase=clase;
