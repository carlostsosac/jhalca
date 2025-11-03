from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, send_from_directory, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from config import SQLALCHEMY_DATABASE_URI, SECRET_KEY, driver as cfg_driver, server as cfg_server, database as cfg_database, username as cfg_username, password as cfg_password, PDF_FOLDER, quote_plus
from models import db, User, Cliente, Mercancia, Tipo, Gasto, AjusteC, AjusteD, FacturaC, FacturaD, ComprasC, ComprasD, CobroC, CobroD, PagoC, PagoD, DevolucionC, DevolucionD, Empresa
from decorators import role_required
import os
from io import BytesIO
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import create_engine, text, or_, and_
from pdf_generator import generate_invoice_pdf, generate_compra_pdf, generate_cobro_pdf, generate_pago_pdf, generate_devolucion_pdf, generate_cobros_report_pdf, generate_pagos_report_pdf
import io
import os
from models import User, Cliente, Proveedor, Mercancia, FacturaC, AjusteD, AjusteC, db
from decorators import role_required
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['PDF_FOLDER'] = PDF_FOLDER

UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.authenticate(username, password)
        if user:
            login_user(user)
            flash('Inicio de sesión exitoso.', 'success')
            return redirect(url_for('index'))
        else:
            flash('Usuario o clave inválida.', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Sesión cerrada.', 'info')
    return redirect(url_for('login'))

# Example route for a generic form page (Clientes)
@app.route('/clientes', methods=['GET','POST'])
@login_required
def clientes():
    if request.method == 'POST':
        cli_id = request.form.get('id')
        nombre = request.form.get('nombre')
        rnc = request.form.get('rnc')
        contacto = request.form.get('contacto')
        telefono = request.form.get('telefono')
        direccion = request.form.get('direccion')
        correo = request.form.get('correo')
        if cli_id:
            try:
                cli = Cliente.query.get(int(cli_id))
                if not cli:
                    flash('Cliente no encontrado.', 'warning')
                    return redirect(url_for('clientes'))
                cli.nombre = nombre
                cli.rnc = rnc
                cli.contacto = contacto
                cli.telefono = telefono
                cli.direccion = direccion
                cli.correo = correo
                db.session.commit()
    
            except Exception as e:
                db.session.rollback()
                flash(f'Error al actualizar cliente: {e}', 'danger')
            return redirect(url_for('clientes'))
        else:
            try:
                nuevo = Cliente(nombre=nombre, rnc=rnc, contacto=contacto, telefono=telefono, direccion=direccion, correo=correo)
                db.session.add(nuevo)
                db.session.commit()
                flash('Cliente guardado correctamente.', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error al guardar cliente: {e}', 'danger')
            return redirect(url_for('clientes'))

    return render_template('clientes.html', page_title='Clientes', form_name='clientes')


# === API: Buscar clientes por nombre ===
@app.route('/api/clientes')
@login_required
def api_clientes():
    q = (request.args.get('q') or '').strip()
    query = Cliente.query
    if q:
        query = query.filter(Cliente.nombre.ilike(f"%{q}%"))
    clientes = query.order_by(Cliente.nombre).limit(50).all()
    return jsonify([
        {
            'id': c.id,
            'nombre': c.nombre,
            'rnc': c.rnc,
            'contacto': c.contacto,
            'telefono': c.telefono,
            'direccion': c.direccion,
            'correo': c.correo,
        } for c in clientes
    ])

@app.route('/api/proveedores')
@login_required
def api_proveedores():
    q = (request.args.get('q') or '').strip()
    query = Proveedor.query
    if q:
        like_pattern = f"%{q}%"
        query = query.filter(or_(
            Proveedor.nombre.ilike(like_pattern),
            Proveedor.rnc.ilike(like_pattern),
            Proveedor.contacto.ilike(like_pattern)
        ))
    proveedores = query.order_by(Proveedor.nombre).limit(50).all()
    return jsonify([
        {
            'id': p.id,
            'nombre': p.nombre,
            'rnc': p.rnc,
            'contacto': p.contacto,
            'telefono': p.telefono,
            'direccion': p.direccion,
            'correo': p.correo,
        } for p in proveedores
    ])

# === API: Obtener un proveedor por id ===
@app.route('/api/proveedores/<int:id>')
@login_required
def api_proveedor(id):
    p = Proveedor.query.get_or_404(id)
    return jsonify({
        'id': p.id,
        'nombre': p.nombre,
        'rnc': p.rnc,
        'contacto': p.contacto,
        'telefono': p.telefono,
        'direccion': p.direccion,
        'correo': p.correo,
    })

# === API: Obtener un cliente por id ===
@app.route('/api/clientes/<int:id>')
@login_required
def api_cliente(id):
    c = Cliente.query.get_or_404(id)
    return jsonify({
        'id': c.id,
        'nombre': c.nombre,
        'rnc': c.rnc,
        'contacto': c.contacto,
        'telefono': c.telefono,
        'direccion': c.direccion,
        'correo': c.correo,
    })

# Example route for proveedores
@app.route('/proveedores', methods=['GET','POST'])
@login_required
def proveedores():
    if request.method == 'POST':
        prov_id = request.form.get('id')
        nombre = request.form.get('nombre')
        rnc = request.form.get('rnc')
        contacto = request.form.get('contacto')
        telefono = request.form.get('telefono')
        direccion = request.form.get('direccion')
        correo = request.form.get('correo')

        if prov_id:
            try:
                prov = Proveedor.query.get(int(prov_id))
                if not prov:
                    flash('Proveedor no encontrado.', 'warning')
                    return redirect(url_for('proveedores'))
                prov.nombre = nombre
                prov.rnc = rnc
                prov.contacto = contacto
                prov.telefono = telefono
                prov.direccion = direccion
                prov.correo = correo
                db.session.commit()
               # flash('Proveedor actualizado correctamente.', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error al actualizar proveedor: {e}', 'danger')
            return redirect(url_for('proveedores'))
        else:
            try:
                nuevo = Proveedor(
                    nombre=nombre,
                    rnc=rnc,
                    contacto=contacto,
                    telefono=telefono,
                    direccion=direccion,
                    correo=correo
                )
                db.session.add(nuevo)
                db.session.commit()
                flash('Proveedor guardado correctamente.', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error al guardar proveedor: {e}', 'danger')
            return redirect(url_for('proveedores'))

    return render_template('proveedores.html', page_title='Proveedores', form_name='proveedores')

# === MERCANCÍAS ===
@app.route('/mercancias', methods=['GET','POST'])
@login_required
def mercancias():
    if request.method == 'POST':
        merc_id = request.form.get('id')
        codigo = request.form.get('codigo')
        nombre = request.form.get('nombre')
        precio = request.form.get('precio')
        existencia = request.form.get('existencia')
        costo = request.form.get('costo')
        tipo = request.form.get('tipo') or 'Inventario'
        clase_id = request.form.get('clase_id')
        
        if merc_id:
            try:
                merc = Mercancia.query.get(int(merc_id))
                if not merc:
                    flash('Mercancía no encontrada.', 'warning')
                    return redirect(url_for('mercancias'))
                merc.codigo = codigo
                merc.nombre = nombre
                merc.precio = float(precio) if precio else 0
                merc.existencia = int(existencia) if existencia else 0
                merc.costo = float(costo) if costo else 0
                merc.tipo = tipo
                merc.clase_id = int(clase_id) if clase_id else None
                db.session.commit()
                #flash('Mercancía actualizada correctamente.', 'success')
            except Exception as e:
                db.session.rollback()
                #flash(f'Error al actualizar mercancía: {e}', 'danger')
            return redirect(url_for('mercancias'))
        else:
            try:
                nueva = Mercancia(
                    codigo=codigo,
                    nombre=nombre,
                    precio=float(precio) if precio else 0,
                    existencia=int(existencia) if existencia else 0,
                    costo=float(costo) if costo else 0,
                    tipo=tipo,
                    clase_id=int(clase_id) if clase_id else None
                )
                db.session.add(nueva)
                db.session.commit()
                flash('Mercancía guardada correctamente.', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error al guardar mercancía: {e}', 'danger')
            return redirect(url_for('mercancias'))

    return render_template('mercancias.html', page_title='Mercancías', form_name='mercancias')



# === AJUSTE DE INVENTARIO ===
@app.route('/ajusteinv', methods=['GET','POST'])
@login_required
def ajusteinv():
    if request.method == 'POST':
        ajuste_id = request.form.get('id')
        codigo = (request.form.get('codigo') or '').strip()
        fecha_str = request.form.get('fecha')
        clase = request.form.get('clase')
        comentario = (request.form.get('comentario') or '').strip()
        estado = request.form.get('estado') or 'activo'

        merc_ids = request.form.getlist('mercancia_id[]')
        cantidades = request.form.getlist('cantidad[]')
        costos = request.form.getlist('costo[]')

        print(f"merc_ids: {merc_ids}")
        print(f"cantidades: {cantidades}")
        #print(f"precios: {precios}")
        print(f"costos: {costos}")

        # Parse fecha
        fecha = None
        try:
            if fecha_str:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except Exception:
            fecha = None

        try:
            # Generar código automático usando la tabla 'secuencias' para clase 'ajuste'
            auto_codigo = codigo
            if not auto_codigo:
                # Asegurar que existe la fila de 'ajuste'; si no, crearla
                try:
                    # Sintaxis para PostgreSQL
                    db.session.execute(text("INSERT INTO secuencias (codigo, secuencia, clase) VALUES ('AJ', 1, 'ajuste') ON CONFLICT (clase) DO NOTHING;"))
                except Exception: # Ignorar si ya existe
                    pass
                
                # Bloquear, leer y actualizar la secuencia
                row = db.session.execute(text("SELECT codigo, secuencia FROM secuencias WHERE clase = :clase FOR UPDATE"), {'clase': 'ajuste'}).fetchone()
                db.session.execute(text("UPDATE secuencias SET secuencia = secuencia + 1 WHERE clase = :clase"), {'clase': 'ajuste'})
                prefix = row[0] if row else 'AJ'
                prev_seq = row[1] if row else 1
                auto_codigo = f"{prefix}{prev_seq:06d}"

            ajuste = AjusteC(
                codigo=auto_codigo,
                fecha=fecha,
                clase=clase,
                comentario=comentario,
                total=0,
                estado=estado
            )
            db.session.add(ajuste)
            db.session.flush()  # obtener id

            total = 0.0
            n = max(len(merc_ids), len(cantidades), len(costos))
            subtotal = 0.0
            for i in range(n):
                try:
                    mid = int(merc_ids[i]) if i < len(merc_ids) and merc_ids[i] else None
                    qty = int(cantidades[i]) if i < len(cantidades) and cantidades[i] else None
                    cst = float(costos[i]) if i < len(costos) and costos[i] else 0.0
                except Exception:
                    mid = None; qty = None; cst = 0.0
                if not mid or qty is None:
                    continue

                detalle = AjusteD(
                    ajuste_id=ajuste.id,
                    mercancia_id=mid,
                    cantidad=qty,
                    costo=cst
                )
                db.session.add(detalle)

                # actualizar existencia de la mercancía
                merc = Mercancia.query.get(mid)
                if merc is not None:
                    try:
                        merc.existencia = int(merc.existencia or 0) + int(qty)
                    except Exception:
                        pass
                total += (cst * (qty or 0))

            ajuste.total = total
            db.session.commit()
            flash('Ajuste de inventario guardado correctamente.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar ajuste: {e}', 'danger')
        return redirect(url_for('ajusteinv'))

    return render_template('ajusteinv.html', page_title='Ajuste de Inventario', form_name='ajusteinv', current_date=date.today())

# === FACTURAS ===
@app.route('/facturas', methods=['GET','POST'])
@login_required
def facturas():
    if request.method == 'POST':
        fac_id = request.form.get('id')
        codigo = (request.form.get('codigo') or '').strip()
        fecha_str = request.form.get('fecha')
        referencia = (request.form.get('referencia') or '').strip()
        condicion = (request.form.get('condicion') or '').strip()
        cliente_id = request.form.get('cliente_id')
        comentario = (request.form.get('comentario') or '').strip()
        estado = (request.form.get('estado') or 'cotizado').strip()
        descuento_str = request.form.get('descuento') or '0'
        subtotal = 0.0

        merc_ids = request.form.getlist('mercancia_id[]')
        cantidades = request.form.getlist('cantidad[]')
        precios = request.form.getlist('precio[]')
        costos = request.form.getlist('costo[]')

        fecha = None
        try:
            if fecha_str:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except Exception:
            fecha = None

        try:
            # Generar código automático usando secuencias (clase 'factura')
            auto_codigo = codigo
            if not auto_codigo:
                try:
                    # Sintaxis para PostgreSQL
                    db.session.execute(text("INSERT INTO secuencias (codigo, secuencia, clase) VALUES ('F', 1, 'factura') ON CONFLICT (clase) DO NOTHING;"))
                except Exception:
                    pass

                # Bloquear, leer y actualizar la secuencia
                row = db.session.execute(text("SELECT codigo, secuencia FROM secuencias WHERE clase = :clase FOR UPDATE"), {'clase': 'factura'}).fetchone()
                db.session.execute(text("UPDATE secuencias SET secuencia = secuencia + 1 WHERE clase = :clase"), {'clase': 'factura'})
                prefix = row[0] if row else 'F'
                prev_seq = row[1] if row else 1
                auto_codigo = f"{prefix}{prev_seq:06d}"

            # Creación o actualización
            factura = None
            if fac_id:
                factura = FacturaC.query.get(int(fac_id))
                if not factura:
                    flash('Factura no encontrada.', 'warning')
                    return redirect(url_for('facturas'))
                factura.codigo = auto_codigo or factura.codigo
                factura.fecha = fecha
                factura.referencia = referencia
                factura.condicion = condicion
                factura.cliente_id = int(cliente_id) if cliente_id else None
                factura.comentario = comentario
                factura.estado = estado
                # eliminar detalles anteriores
                FacturaD.query.filter_by(factura_id=factura.id).delete()
            else:
                factura = FacturaC(
                    codigo=auto_codigo,
                    fecha=fecha,
                    referencia=referencia,
                    condicion=condicion,
                    cliente_id=int(cliente_id) if cliente_id else None,
                    comentario=comentario,
                    estado=estado,
                )
                db.session.add(factura)
                db.session.flush()

            subtotal = 0.0
            n = max(len(merc_ids), len(cantidades), len(precios), len(costos))
            for i in range(n):
                try:
                    mid = int(merc_ids[i]) if i < len(merc_ids) and merc_ids[i] else None
                    qty = float(cantidades[i]) if i < len(cantidades) and cantidades[i] else None
                    prc = float(precios[i]) if i < len(precios) and precios[i] else 0.0
                    cst = float(costos[i]) if i < len(costos) and costos[i] else 0.0
                except Exception:
                    mid = None; qty = None; prc = 0.0; cst = 0.0
                if not mid or qty is None:
                    continue

                imp = prc * (qty or 0)
                detalle = FacturaD(
                    factura_id=factura.id,
                    mercancia_id=mid,
                    cantidad=int(qty),
                    precio=prc,
                    costo=cst,
                    importe=imp
                )
                db.session.add(detalle)
                print(f"Detalle agregado: {detalle.mercancia_id}, {detalle.cantidad}, {detalle.precio}, {detalle.costo}, {detalle.importe}")
                subtotal += imp

            try:
                descuento = float(descuento_str) if descuento_str else 0.0
            except Exception:
                descuento = 0.0
            base_itbis = max(subtotal - descuento, 0.0)
            itbis = round(base_itbis * 0.18, 2)
            total = round(subtotal - descuento + itbis, 2)

            factura.subtotal = subtotal
            factura.descuento = descuento
            factura.itbis = itbis
            factura.total = total

            # Actualizar el balance según la condición
            if condicion == 'credito':
                factura.balance = total
            else:
                factura.balance = 0.0

            # Afectar inventario solo al facturar (no en cotización)
            afectar_inventario = False
            if fac_id:
                # si transiciona de cotizado a facturado
                try:
                    prev = db.session.execute(text("SELECT estado FROM facturasc WHERE id = :id"), { 'id': factura.id }).scalar()
                    if prev != 'facturado' and estado == 'facturado':
                        afectar_inventario = True
                except Exception:
                    afectar_inventario = (estado == 'facturado')
            else:
                afectar_inventario = (estado == 'facturado')

            # Actualizar inventario al guardar la factura
            detalles = factura.detalles  # Usar relación directa
            for d in detalles:
                merc = Mercancia.query.get(d.mercancia_id)
                if merc:
                    merc.existencia = (merc.existencia or 0) - d.cantidad
                    # Advertencia si la existencia es negativa
                    if merc.existencia < 0:
                        flash(f"Advertencia: Existencia de '{merc.nombre}' es negativa ({merc.existencia}).", 'warning')

            db.session.commit()
            

            # Generar PDF de la factura
            try:
                # Obtener datos completos de la factura para el PDF
                factura_completa = FacturaC.query.get(factura.id)
                empresa = Empresa.query.get(1) # Obtener datos de la empresa
                cliente_factura = Cliente.query.get(factura_completa.cliente_id)

                logo_path = None
                if empresa and empresa.logo:
                    logo_path = os.path.join(app.config['UPLOAD_FOLDER'], empresa.logo)
                    if not os.path.exists(logo_path):
                        logo_path = None # No pasar la ruta si el archivo no existe

                invoice_data = {
                    'codigo': factura_completa.codigo,
                    'empresa_nombre': empresa.nombrec if empresa else 'Mi Empresa',
                    'empresa_rnc': empresa.rnc if empresa else '',
                    'empresa_direccion': empresa.direccionc if empresa else '',
                    'empresa_logo_path': logo_path,
                    'fecha': factura_completa.fecha.strftime('%Y-%m-%d'),
                    'cliente_nombre': cliente_factura.nombre if cliente_factura else 'N/A',
                    'cliente_rnc': cliente_factura.rnc if cliente_factura else 'N/A',
                    'condicion': factura_completa.condicion,
                    'comentario': factura_completa.comentario,
                    'subtotal': factura_completa.subtotal,
                    'descuento': factura_completa.descuento,
                    'itbis': factura_completa.itbis,
                    'total': factura_completa.total,
                    'detalles': []
                }

                detalles_factura = FacturaD.query.filter_by(factura_id=factura.id).all()
                for det in detalles_factura:
                    mercancia_detalle = Mercancia.query.get(det.mercancia_id)
                    invoice_data['detalles'].append({
                        'mercancia_codigo': mercancia_detalle.codigo if mercancia_detalle else 'N/A',
                        'mercancia_nombre': mercancia_detalle.nombre if mercancia_detalle else 'N/A',
                        'cantidad': det.cantidad,
                        'precio': det.precio,
                        'importe': det.importe
                    })

                # Generar el PDF en memoria
                buffer = io.BytesIO()
                generate_invoice_pdf(invoice_data, buffer)
                buffer.seek(0)

                pdf_filename = f"factura_{factura.codigo}.pdf"
                pdf_path = os.path.join(app.root_path, 'static', 'pdfs', pdf_filename)

                # Asegurarse de que el directorio static/pdfs exista
                os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

                with open(pdf_path, 'wb') as f:
                    f.write(buffer.getvalue())

                flash(f'Factura guardada correctamente. PDF generado: {pdf_filename}', 'success')
                return redirect(url_for('facturas'))

            except Exception as e:
                flash(f'Error al generar PDF de la factura: {e}', 'warning')
                return redirect(url_for('facturas'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar factura: {e}', 'danger')
        return redirect(url_for('facturas'))

    return render_template('facturas.html', page_title='Facturas', form_name='facturas', current_date=date.today())



# === API: Buscar facturas ===
@app.route('/api/facturas')
@login_required
def api_facturas():
    q = (request.args.get('q') or '').strip()
    cliente_id = request.args.get('cliente_id')
    query = FacturaC.query.join(Cliente, FacturaC.cliente_id == Cliente.id, isouter=True)

    if cliente_id:
        query = query.filter(FacturaC.cliente_id == cliente_id)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(
            FacturaC.codigo.ilike(like), 
            FacturaC.comentario.ilike(like),
            Cliente.nombre.ilike(like)
        ))
    filas = query.order_by(FacturaC.fecha.desc(), FacturaC.codigo.desc()).limit(50).all()
    result = []
    for f in filas:
        cli = Cliente.query.get(f.cliente_id) if f.cliente_id else None
        result.append({
            'id': f.id,
            'codigo': f.codigo,
            'fecha': f.fecha.isoformat() if f.fecha else None,
            'referencia': f.referencia,
            'condicion': f.condicion,
            'cliente_id': f.cliente_id,
            'cliente_nombre': cli.nombre if cli else None,
            'cliente_rnc': cli.rnc if cli else None,
            'comentario': f.comentario,
            'estado': f.estado,
            'subtotal': float(f.subtotal or 0),
            'itbis': float(f.itbis or 0),
            'descuento': float(f.descuento or 0),
            'total': float(f.total or 0),
            'detalles': [{
                'id': d.id,
                'mercancia_id': d.mercancia_id,
                'mercancia_codigo': d.mercancia.codigo if d.mercancia else None,
                'mercancia_nombre': d.mercancia.nombre if d.mercancia else None,
                'existencia': d.mercancia.existencia if d.mercancia else None,
                'cantidad': int(d.cantidad or 0),
                'precio': float(d.precio or 0),
                'costo': float(d.costo or 0),
                'importe': float(d.importe or 0),
            } for d in f.detalles]
        })
    return jsonify(result)

# === API: Obtener factura por id (incluye detalles) ===
@app.route('/api/facturas/<int:id>')
@login_required
def api_factura(id):
    f = FacturaC.query.get_or_404(id)
    cli = Cliente.query.get(f.cliente_id) if f.cliente_id else None
    detalles = FacturaD.query.filter_by(factura_id=f.id).all()
    det_out = []
    for d in detalles:
        m = Mercancia.query.get(d.mercancia_id)
        det_out.append({
            'id': d.id,
            'mercancia_id': d.mercancia_id,
            'mercancia_codigo': m.codigo if m else None,
            'mercancia_nombre': m.nombre if m else None,
            'existencia': m.existencia if m else None,
            'cantidad': int(d.cantidad or 0),
            'precio': float(d.precio or 0),
            'costo': float(d.costo or 0),
            'importe': float(d.importe or 0),
        })
    return jsonify({
        'id': f.id,
        'codigo': f.codigo,
        'fecha': f.fecha.isoformat() if f.fecha else None,
        'referencia': f.referencia,
        'condicion': f.condicion,
        'cliente_id': f.cliente_id,
        'cliente_nombre': cli.nombre if cli else None,
        'cliente_rnc': cli.rnc if cli else None,
        'comentario': f.comentario,
        'estado': f.estado,
        'subtotal': float(f.subtotal or 0),
        'itbis': float(f.itbis or 0),
        'descuento': float(f.descuento or 0),
        'total': float(f.total or 0),
        'detalles': det_out,
    })

# === DEVOLUCIONES ===
@app.route('/devoluciones', methods=['GET','POST'])
@login_required
def devoluciones():
    origen = request.args.get('origen', 'venta') # Por defecto 'venta'

    if request.method == 'POST':
        try:
            data = request.form
            tipo = data.get('tipo')
            
            # Generar código automático
            clase_secuencia = 'devolucion_venta' if tipo == 'venta' else 'devolucion_compra'
            prefix_default = 'DV' if tipo == 'venta' else 'DC'
            
            try:
                # Sintaxis para PostgreSQL
                db.session.execute(text(f"INSERT INTO secuencias (codigo, secuencia, clase) VALUES ('{prefix_default}', 1, '{clase_secuencia}') ON CONFLICT (clase) DO NOTHING;"))
            except Exception:
                pass
            
            row = db.session.execute(text("SELECT codigo, secuencia FROM secuencias WHERE clase = :clase FOR UPDATE"), {'clase': clase_secuencia}).fetchone()
            db.session.execute(text("UPDATE secuencias SET secuencia = secuencia + 1 WHERE clase = :clase"), {'clase': clase_secuencia})
            prefix = row[0] if row else prefix_default
            prev_seq = row[1] if row else 1
            auto_codigo = f"{prefix}{prev_seq:06d}"

            # Crear encabezado de la devolución
            devolucion = DevolucionC(
                codigo=auto_codigo,
                fecha=datetime.strptime(data.get('fecha'), '%Y-%m-%d').date(),
                tipo=tipo,
                cliente_id=data.get('cliente_id') if tipo == 'venta' else None,
                proveedor_id=data.get('proveedor_id') if tipo == 'compra' else None,
                comentario=data.get('comentario'),
                estado=data.get('estado', 'activa')
            )
            db.session.add(devolucion)
            db.session.flush()

            subtotal = Decimal('0.0')
            mercancia_ids = data.getlist('mercancia_id[]')
            cantidades = data.getlist('cantidad[]')
            precios = data.getlist('precio[]')
            factura_ids = data.getlist('factura_id[]')
            compra_ids = data.getlist('compra_id[]')

            for i in range(len(mercancia_ids)):
                cantidad = Decimal(cantidades[i])
                precio = Decimal(precios[i])
                importe = cantidad * precio
                subtotal += importe

                detalle = DevolucionD(
                    devolucion_id=devolucion.id,
                    mercancia_id=int(mercancia_ids[i]),
                    cantidad=int(cantidad),
                    precio=precio,
                    importe=importe,
                    factura_id=int(factura_ids[i]) if tipo == 'venta' and i < len(factura_ids) and factura_ids[i] else None,
                    compra_id=int(compra_ids[i]) if tipo == 'compra' and i < len(compra_ids) and compra_ids[i] else None
                )
                db.session.add(detalle)

                # Afectar inventario y balances
                mercancia = Mercancia.query.get(int(mercancia_ids[i]))
                if not mercancia: continue

                if tipo == 'venta':
                    # Devolución de venta AUMENTA el inventario
                    mercancia.existencia = (mercancia.existencia or 0) + int(cantidad)
                    # Afectar balance de factura (Nota de Crédito)
                    if detalle.factura_id:
                        factura_afectada = FacturaC.query.get(detalle.factura_id)
                        if factura_afectada:
                            factura_afectada.balance = (factura_afectada.balance or Decimal('0.0')) - importe
                
                elif tipo == 'compra':
                    # Devolución de compra DISMINUYE el inventario
                    mercancia.existencia = (mercancia.existencia or 0) - int(cantidad)
                    # Afectar balance de compra (Nota de Débito)
                    if detalle.compra_id:
                        compra_afectada = ComprasC.query.get(detalle.compra_id)
                        if compra_afectada:
                            compra_afectada.balance = (compra_afectada.balance or Decimal('0.0')) - importe

            # Calcular totales
            itbis = subtotal * Decimal('0.18')
            total = subtotal + itbis
            devolucion.subtotal = subtotal
            devolucion.itbis = itbis
            devolucion.total = total

            db.session.commit()

            # Generar PDF de la devolución
            try:
                devolucion_completa = DevolucionC.query.get(devolucion.id)
                empresa = Empresa.query.get(1)
                logo_path = None
                if empresa and empresa.logo:
                    logo_path = os.path.join(app.config['UPLOAD_FOLDER'], empresa.logo)
                    if not os.path.exists(logo_path):
                        logo_path = None

                devolucion_data = {
                    'codigo': devolucion_completa.codigo,
                    'fecha': devolucion_completa.fecha.strftime('%Y-%m-%d'),
                    'tipo': devolucion_completa.tipo,
                    'comentario': devolucion_completa.comentario,
                    'subtotal': float(devolucion_completa.subtotal),
                    'empresa_nombre': empresa.nombrec if empresa else 'Mi Empresa',
                    'empresa_rnc': empresa.rnc if empresa else '',
                    'empresa_direccion': empresa.direccionc if empresa else '',
                    'empresa_logo_path': logo_path,
                    'itbis': float(devolucion_completa.itbis),
                    'total': float(devolucion_completa.total),
                    'detalles': []
                }
                if devolucion_completa.tipo == 'venta':
                    devolucion_data['cliente_nombre'] = devolucion_completa.cliente.nombre if devolucion_completa.cliente else 'N/A'
                    devolucion_data['cliente_rnc'] = devolucion_completa.cliente.rnc if devolucion_completa.cliente else 'N/A'
                else:
                    devolucion_data['proveedor_nombre'] = devolucion_completa.proveedor.nombre if devolucion_completa.proveedor else 'N/A'
                    devolucion_data['proveedor_rnc'] = devolucion_completa.proveedor.rnc if devolucion_completa.proveedor else 'N/A'

                for det in devolucion_completa.detalles:
                    doc_origen = det.factura if det.factura else det.compra
                    devolucion_data['detalles'].append({
                        'documento_origen_codigo': doc_origen.codigo if doc_origen else 'N/A',
                        'mercancia_codigo': det.mercancia.codigo,
                        'mercancia_nombre': det.mercancia.nombre,
                        'cantidad': det.cantidad,
                        'precio': float(det.precio),
                        'importe': float(det.importe)
                    })

                buffer = io.BytesIO()
                generate_devolucion_pdf(devolucion_data, buffer)
                buffer.seek(0)

                pdf_filename = f"devolucion_{devolucion_completa.codigo}.pdf"
                pdf_path = os.path.join(app.config['PDF_FOLDER'], pdf_filename)
                os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
                with open(pdf_path, 'wb') as f:
                    f.write(buffer.getvalue())

                flash(f'Devolución {auto_codigo} guardada correctamente. PDF generado: {pdf_filename}', 'success')

            except Exception as e:
                flash(f'Devolución guardada, pero hubo un error al generar el PDF: {e}', 'warning')

        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar la devolución: {e}', 'danger')
        
        return redirect(url_for('devoluciones'))

    return render_template('devoluciones.html', page_title='Devoluciones', form_name='devoluciones', current_date=date.today(), origen=origen)

# === COBROS (CUENTAS POR COBRAR) ===
@app.route('/cobros', methods=['GET','POST'])
@login_required
def cobros():
    if request.method == 'POST':
        cobro_id = request.form.get('id')
        codigo = (request.form.get('codigo') or '').strip()
        fecha_str = request.form.get('fecha')
        cliente_id = request.form.get('cliente_id')
        forma_pago = request.form.get('forma_pago')
        comentario = (request.form.get('comentario') or '').strip()
        estado = request.form.get('estado') or 'activo'

        factura_ids = request.form.getlist('factura_id[]')
        aplicados = request.form.getlist('aplicado[]')
        descuentos = request.form.getlist('descuento[]')
        cargos = request.form.getlist('cargo[]')

        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date() if fecha_str else date.today()

        try:
            # Generar código automático para el cobro
            auto_codigo = codigo
            if not auto_codigo:
                # Usar una secuencia para 'cobro'
                try:
                    db.session.execute(text("INSERT INTO secuencias (codigo, secuencia, clase) VALUES ('RC', 1, 'cobro') ON CONFLICT (clase) DO NOTHING;"))
                except Exception:
                    pass
                row = db.session.execute(text("SELECT codigo, secuencia FROM secuencias WHERE clase = :clase FOR UPDATE"), {'clase': 'cobro'}).fetchone()
                db.session.execute(text("UPDATE secuencias SET secuencia = secuencia + 1 WHERE clase = :clase"), {'clase': 'cobro'})
                prefix = row[0] if row else 'RC'
                prev_seq = row[1] if row else 1
                auto_codigo = f"{prefix}{prev_seq:06d}"

            # Crear encabezado del cobro
            cobro = CobroC(
                codigo=auto_codigo,
                fecha=fecha,
                cliente_id=int(cliente_id) if cliente_id else None,
                forma_pago=forma_pago,
                comentario=comentario,
                estado=estado
            )
            db.session.add(cobro)
            db.session.flush() # Para obtener el ID del cobro

            total_aplicado = Decimal('0.0')
            total_descuentos = Decimal('0.0')
            total_cargos = Decimal('0.0')

            for i in range(len(factura_ids)):
                fact_id = int(factura_ids[i])
                monto_aplicado = Decimal(aplicados[i] or '0')
                monto_descuento = Decimal(descuentos[i] or '0')
                monto_cargo = Decimal(cargos[i] or '0')

                if monto_aplicado <= 0:
                    continue

                # Crear detalle del cobro
                detalle = CobroD(
                    cobro_id=cobro.id,
                    factura_id=fact_id,
                    aplicado=monto_aplicado,
                    descuento=monto_descuento,
                    cargo=monto_cargo
                )
                db.session.add(detalle)

                # Actualizar el balance de la factura
                factura_afectada = FacturaC.query.get(fact_id)
                if factura_afectada:
                    factura_afectada.balance = (factura_afectada.balance or Decimal('0.0')) - monto_aplicado

                total_aplicado += monto_aplicado
                total_descuentos += monto_descuento
                total_cargos += monto_cargo

            cobro.total = total_aplicado
            cobro.descuentos = total_descuentos
            cobro.cargos = total_cargos

            db.session.commit()

            # Generar PDF del recibo de cobro
            try:
                empresa = Empresa.query.get(1)
                cliente_cobro = Cliente.query.get(cobro.cliente_id)
                logo_path = None
                if empresa and empresa.logo:
                    logo_path = os.path.join(app.config['UPLOAD_FOLDER'], empresa.logo)
                    if not os.path.exists(logo_path):
                        logo_path = None

                cobro_data = {
                    'codigo': cobro.codigo,
                    'fecha': cobro.fecha.strftime('%Y-%m-%d'),
                    'cliente_nombre': cliente_cobro.nombre if cliente_cobro else 'N/A',
                    'cliente_rnc': cliente_cobro.rnc if cliente_cobro else 'N/A',
                    'empresa_nombre': empresa.nombrec if empresa else 'Mi Empresa',
                    'empresa_rnc': empresa.rnc if empresa else '',
                    'empresa_direccion': empresa.direccionc if empresa else '',
                    'empresa_logo_path': logo_path,
                    'forma_pago': cobro.forma_pago,
                    'comentario': cobro.comentario,
                    'total': cobro.total,
                    'detalles': []
                }
                for det in cobro.detalles:
                    cobro_data['detalles'].append({
                        'factura_codigo': det.factura.codigo,
                        'aplicado': det.aplicado,
                        'descuento': det.descuento,
                        'cargo': det.cargo
                    })

                buffer = io.BytesIO()
                generate_cobro_pdf(cobro_data, buffer)
                buffer.seek(0)

                pdf_filename = f"cobro_{cobro.codigo}.pdf"
                pdf_path = os.path.join(app.config['PDF_FOLDER'], pdf_filename)
                os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
                with open(pdf_path, 'wb') as f:
                    f.write(buffer.getvalue())

                flash(f'Cobro guardado correctamente. PDF generado: {pdf_filename}', 'success')
            except Exception as e:
                flash(f'Error al generar PDF del cobro: {e}', 'warning')

        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar el cobro: {e}', 'danger')
        
        return redirect(url_for('cobros'))

    return render_template('cobros.html', page_title='Cobros', form_name='cobros', current_date=date.today())

@app.route('/cobros/reporte_pdf')
@login_required
def cobros_reporte_pdf():
    desde_str = request.args.get('desde')
    hasta_str = request.args.get('hasta')
    
    query = CobroC.query.join(Cliente, CobroC.cliente_id == Cliente.id, isouter=True)

    if desde_str:
        query = query.filter(CobroC.fecha >= datetime.strptime(desde_str, '%Y-%m-%d').date())
    if hasta_str:
        query = query.filter(CobroC.fecha <= datetime.strptime(hasta_str, '%Y-%m-%d').date())
    
    cobros = query.order_by(CobroC.fecha.asc(), CobroC.codigo.asc()).all()

    buffer = io.BytesIO()
    generate_cobros_report_pdf(cobros, buffer, desde_str, hasta_str)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name='reporte_de_cobros.pdf',
        mimetype='application/pdf'
    )
# === PAGOS (CUENTAS POR PAGAR) ===
@app.route('/pagos', methods=['GET','POST'])
@login_required
def pagos():
    if request.method == 'POST':
        pago_id = request.form.get('id')
        codigo = (request.form.get('codigo') or '').strip()
        fecha_str = request.form.get('fecha')
        proveedor_id = request.form.get('proveedor_id')
        forma_pago = request.form.get('forma_pago')
        comentario = (request.form.get('comentario') or '').strip()
        estado = request.form.get('estado') or 'activo'

        compra_ids = request.form.getlist('compra_id[]')
        aplicados = request.form.getlist('aplicado[]')
        descuentos = request.form.getlist('descuento[]')
        cargos = request.form.getlist('cargo[]')

        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date() if fecha_str else date.today()

        try:
            auto_codigo = codigo
            if not auto_codigo:
                try:
                    db.session.execute(text("INSERT INTO secuencias (codigo, secuencia, clase) VALUES ('PA', 1, 'pago') ON CONFLICT (clase) DO NOTHING;"))
                except Exception:
                    pass

                row = db.session.execute(text("SELECT codigo, secuencia FROM secuencias WHERE clase = :clase FOR UPDATE"), {'clase': 'pago'}).fetchone()
                db.session.execute(text("UPDATE secuencias SET secuencia = secuencia + 1 WHERE clase = :clase"), {'clase': 'pago'})
                prefix = row[0] if row else 'PA'
                prev_seq = row[1] if row else 1
                auto_codigo = f"{prefix}{prev_seq:06d}"

            pago = PagoC(
                codigo=auto_codigo,
                fecha=fecha,
                proveedor_id=int(proveedor_id) if proveedor_id else None,
                forma_pago=forma_pago,
                comentario=comentario,
                estado=estado
            )
            db.session.add(pago)
            db.session.flush()

            total_aplicado = Decimal('0.0')
            total_descuentos = Decimal('0.0')
            total_cargos = Decimal('0.0')

            for i in range(len(compra_ids)):
                compra_id = int(compra_ids[i])
                monto_aplicado = Decimal(aplicados[i] or '0')
                monto_descuento = Decimal(descuentos[i] or '0')
                monto_cargo = Decimal(cargos[i] or '0')

                if monto_aplicado <= 0:
                    continue

                detalle = PagoD(
                    pago_id=pago.id,
                    compra_id=compra_id,
                    aplicado=monto_aplicado,
                    descuento=monto_descuento,
                    cargo=monto_cargo
                )
                db.session.add(detalle)

                compra_afectada = ComprasC.query.get(compra_id)
                if compra_afectada:
                    compra_afectada.balance = (compra_afectada.balance or Decimal('0.0')) - monto_aplicado

                total_aplicado += monto_aplicado
                total_descuentos += monto_descuento
                total_cargos += monto_cargo

            pago.total = total_aplicado
            pago.descuentos = total_descuentos
            pago.cargos = total_cargos

            db.session.commit()

            try:
                empresa = Empresa.query.get(1)
                proveedor_pago = Proveedor.query.get(pago.proveedor_id)
                logo_path = None
                if empresa and empresa.logo:
                    logo_path = os.path.join(app.config['UPLOAD_FOLDER'], empresa.logo)
                    if not os.path.exists(logo_path):
                        logo_path = None

                pago_data = {
                    'codigo': pago.codigo,
                    'fecha': pago.fecha.strftime('%Y-%m-%d'),
                    'proveedor_nombre': proveedor_pago.nombre if proveedor_pago else 'N/A',
                    'proveedor_rnc': proveedor_pago.rnc if proveedor_pago else 'N/A',
                    'empresa_nombre': empresa.nombrec if empresa else 'Mi Empresa',
                    'empresa_rnc': empresa.rnc if empresa else '',
                    'empresa_direccion': empresa.direccionc if empresa else '',
                    'empresa_logo_path': logo_path,
                    'forma_pago': pago.forma_pago,
                    'comentario': pago.comentario,
                    'total': pago.total,
                    'detalles': []
                }
                for det in pago.detalles:
                    pago_data['detalles'].append({
                        'compra_codigo': det.compra.codigo,
                        'aplicado': det.aplicado,
                        'descuento': det.descuento,
                        'cargo': det.cargo
                    })

                buffer = io.BytesIO()
                generate_pago_pdf(pago_data, buffer)
                buffer.seek(0)

                pdf_filename = f"pago_{pago.codigo}.pdf"
                pdf_path = os.path.join(app.config['PDF_FOLDER'], pdf_filename)
                os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
                with open(pdf_path, 'wb') as f:
                    f.write(buffer.getvalue())

                flash(f'Pago guardado correctamente. PDF generado: {pdf_filename}', 'success')
            except Exception as e:
                flash(f'Error al generar PDF del pago: {e}', 'warning')

        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar el pago: {e}', 'danger')
        
        return redirect(url_for('pagos'))

    return render_template('pagos.html', page_title='Pagos a Proveedores', form_name='pagos', current_date=date.today())

@app.route('/pagos/reporte_pdf')
@login_required
def pagos_reporte_pdf():
    desde_str = request.args.get('desde')
    hasta_str = request.args.get('hasta')
    
    query = PagoC.query.join(Proveedor, PagoC.proveedor_id == Proveedor.id, isouter=True)

    if desde_str:
        query = query.filter(PagoC.fecha >= datetime.strptime(desde_str, '%Y-%m-%d').date())
    if hasta_str:
        query = query.filter(PagoC.fecha <= datetime.strptime(hasta_str, '%Y-%m-%d').date())
    
    pagos = query.order_by(PagoC.fecha.asc(), PagoC.codigo.asc()).all()

    buffer = io.BytesIO()
    generate_pagos_report_pdf(pagos, buffer, desde_str, hasta_str)
    buffer.seek(0)
    
    return send_file(
        buffer,
        as_attachment=True,
        download_name='reporte_de_pagos.pdf',
        mimetype='application/pdf'
    )

# === API: Buscar facturas con balance pendiente por cliente ===
@app.route('/api/facturas_por_cobrar')
@login_required
def api_facturas_por_cobrar():
    cliente_id = request.args.get('cliente_id')
    if not cliente_id:
        return jsonify([])
    
    facturas = FacturaC.query.filter(and_(FacturaC.cliente_id == cliente_id, FacturaC.balance > 0)).order_by(FacturaC.fecha.asc()).all()
    
    return jsonify([{
        'id': f.id,
        'codigo': f.codigo,
        'fecha': f.fecha.isoformat(),
        'total': float(f.total),
        'balance': float(f.balance)
    } for f in facturas])

@app.route('/api/compras_por_pagar')
@login_required
def api_compras_por_pagar():
    proveedor_id = request.args.get('proveedor_id')
    if not proveedor_id:
        return jsonify([])
    
    compras = ComprasC.query.filter(and_(ComprasC.proveedor_id == proveedor_id, ComprasC.balance > 0)).order_by(ComprasC.fecha.asc()).all()
    
    return jsonify([{
        'id': c.id,
        'codigo': c.codigo,
        'fecha': c.fecha.isoformat(),
        'total': float(c.total),
        'balance': float(c.balance)
    } for c in compras])

# === API: Buscar pagos ===
@app.route('/api/pagos')
@login_required
def api_pagos():
    q = (request.args.get('q') or '').strip()
    query = PagoC.query
    if q:
        like = f"%{q}%"
        query = query.filter(or_(
            PagoC.codigo.ilike(like),
            PagoC.comentario.ilike(like)
        ))
    
    filas = query.order_by(PagoC.fecha.desc(), PagoC.codigo.desc()).limit(50).all()
    result = []
    for p in filas:
        prov = Proveedor.query.get(p.proveedor_id) if p.proveedor_id else None
        result.append({
            'id': p.id,
            'codigo': p.codigo,
            'fecha': p.fecha.isoformat() if p.fecha else None,
            'proveedor_nombre': prov.nombre if prov else None,
            'total': float(p.total or 0),
        })
    return jsonify(result)

# === API: Reporte de facturas pendientes agrupadas por cliente ===
@app.route('/api/reportes/facturas_pendientes_agrupadas')
@login_required
def api_reporte_facturas_pendientes():
    facturas_pendientes = db.session.query(FacturaC, Cliente)\
        .join(Cliente, FacturaC.cliente_id == Cliente.id)\
        .filter(FacturaC.balance > 0)\
        .order_by(Cliente.nombre, FacturaC.fecha)\
        .all()

    clientes = {}
    for factura, cliente in facturas_pendientes:
        if cliente.id not in clientes:
            clientes[cliente.id] = {
                'id': cliente.id,
                'nombre': cliente.nombre,
                'rnc': cliente.rnc,
                'facturas': [],
                'total_balance': Decimal('0.0')
            }
        
        clientes[cliente.id]['facturas'].append({
            'codigo': factura.codigo,
            'fecha': factura.fecha.isoformat(),
            'balance': float(factura.balance)
        })
        clientes[cliente.id]['total_balance'] += factura.balance

    return jsonify(list(clientes.values()))

# === API: Reporte de compras pendientes agrupadas por proveedor ===
@app.route('/api/reportes/compras_pendientes_agrupadas')
@login_required
def api_reporte_compras_pendientes():
    compras_pendientes = db.session.query(ComprasC, Proveedor)\
        .join(Proveedor, ComprasC.proveedor_id == Proveedor.id)\
        .filter(ComprasC.balance > 0)\
        .order_by(Proveedor.nombre, ComprasC.fecha)\
        .all()

    proveedores = {}
    for compra, proveedor in compras_pendientes:
        if proveedor.id not in proveedores:
            proveedores[proveedor.id] = {
                'id': proveedor.id,
                'nombre': proveedor.nombre,
                'rnc': proveedor.rnc,
                'compras': [],
                'total_balance': Decimal('0.0')
            }
        
        proveedores[proveedor.id]['compras'].append({
            'codigo': compra.codigo,
            'fecha': compra.fecha.isoformat(),
            'balance': float(compra.balance)
        })
        proveedores[proveedor.id]['total_balance'] += compra.balance

    return jsonify(list(proveedores.values()))

# === COMPRAS ===
@app.route('/compras', methods=['GET','POST'])
@login_required
def compras():
    if request.method == 'POST':
        com_id = request.form.get('id')
        codigo = (request.form.get('codigo') or '').strip()
        fecha_str = request.form.get('fecha')
        referencia = (request.form.get('referencia') or '').strip()
        condicion = (request.form.get('condicion') or '').strip()
        proveedor_id = request.form.get('proveedor_id')
        comentario = (request.form.get('comentario') or '').strip()
        estado = (request.form.get('estado') or 'facturado').strip()
        descuento_str = request.form.get('descuento') or '0'
        subtotal = 0.0

        merc_ids = request.form.getlist('mercancia_id[]')
        cantidades = request.form.getlist('cantidad[]')
        precios = request.form.getlist('precio[]')
        costos = request.form.getlist('costo[]')

        fecha = None
        try:
            if fecha_str:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except Exception:
            fecha = None

        try:
            # Generar código automático usando secuencias (clase 'compra')
            auto_codigo = codigo
            if not auto_codigo:
                try:
                    db.session.execute(text("INSERT INTO secuencias (codigo, secuencia, clase) VALUES ('CM', 1, 'compra') ON CONFLICT (clase) DO NOTHING;"))
                except Exception:
                    pass

                row = db.session.execute(text("SELECT codigo, secuencia FROM secuencias WHERE clase = :clase FOR UPDATE"), {'clase': 'compra'}).fetchone()
                db.session.execute(text("UPDATE secuencias SET secuencia = secuencia + 1 WHERE clase = :clase"), {'clase': 'compra'})
                prefix = (row[0] if row else 'CM')
                prev_seq = (row[1] if row else 1)
                auto_codigo = f"{prefix}{prev_seq:06d}"

            # Creación o actualización
            compra = None
            if com_id:
                compra = ComprasC.query.get(int(com_id))
                if not compra:
                    flash('Compra no encontrada.', 'warning')
                    return redirect(url_for('compras'))
                compra.codigo = auto_codigo or compra.codigo
                compra.fecha = fecha
                compra.referencia = referencia
                compra.condicion = condicion
                compra.proveedor_id = int(proveedor_id) if proveedor_id else None
                compra.comentario = comentario
                compra.estado = estado
                # eliminar detalles anteriores
                ComprasD.query.filter_by(compra_id=compra.id).delete()
            else:
                compra = ComprasC(
                    codigo=auto_codigo,
                    fecha=fecha,
                    referencia=referencia,
                    condicion=condicion,
                    proveedor_id=int(proveedor_id) if proveedor_id else None,
                    comentario=comentario,
                    estado=estado,
                )
                db.session.add(compra)
                db.session.flush()

            subtotal = 0.0
            n = max(len(merc_ids), len(cantidades), len(precios), len(costos))
            for i in range(n):
                try:
                    mid = int(merc_ids[i]) if i < len(merc_ids) and merc_ids[i] else None
                    qty = float(cantidades[i]) if i < len(cantidades) and cantidades[i] else None
                    prc = float(precios[i]) if i < len(precios) and precios[i] else 0.0
                    cst = float(costos[i]) if i < len(costos) and costos[i] else 0.0
                except Exception:
                    mid = None; qty = None; prc = 0.0; cst = 0.0
                if not mid or qty is None:
                    continue

                imp = prc * (qty or 0)
                detalle = ComprasD(
                    compra_id=compra.id,
                    mercancia_id=mid,
                    cantidad=int(qty),
                    precio=prc,
                    costo=cst,
                    importe=imp
                )
                db.session.add(detalle)
                print(f"Detalle agregado: {detalle.mercancia_id}, {detalle.cantidad}, {detalle.precio}, {detalle.costo}, {detalle.importe}")
                subtotal += imp

            try:
                descuento = float(descuento_str) if descuento_str else 0.0
            except Exception:
                descuento = 0.0
            base_itbis = max(subtotal - descuento, 0.0)
            itbis = round(base_itbis * 0.18, 2)
            total = round(subtotal - descuento + itbis, 2)

            compra.subtotal = subtotal
            compra.descuento = descuento
            compra.itbis = itbis
            compra.total = total

            # Actualizar el balance según la condición
            if condicion == 'credito':
                compra.balance = total
            else:
                compra.balance = 0.0

            # Afectar inventario solo al comprar (no en cotización)
            afectar_inventario = False
            if com_id:
                # si transiciona de cotizado a comprado
                try:
                    prev = db.session.execute(text("SELECT estado FROM comprasc WHERE id = :id"), { 'id': compra.id }).scalar()
                    if prev != 'comprado' and estado == 'comprado':
                        afectar_inventario = True
                except Exception:
                    afectar_inventario = (estado == 'comprado')
            else:
                afectar_inventario = (estado == 'comprado')

            # Actualizar inventario al guardar la compra
            detalles = compra.detalles  # Usar relación directa
            for d in detalles:
                merc = Mercancia.query.get(d.mercancia_id)
                if merc:
                    merc.existencia = (merc.existencia or 0) + d.cantidad
                    # Advertencia si la existencia es negativa
                    if merc.existencia < 0:
                        flash(f"Advertencia: Existencia de '{merc.nombre}' es negativa ({merc.existencia}).", 'warning')

            db.session.commit()
            

            # Generar PDF de la compra
            try:
                # Obtener datos completos de la compra para el PDF
                compra_completa = ComprasC.query.get(compra.id)
                empresa = Empresa.query.get(1)
                proveedor_compra = Proveedor.query.get(compra_completa.proveedor_id)
                logo_path = None
                if empresa and empresa.logo:
                    logo_path = os.path.join(app.config['UPLOAD_FOLDER'], empresa.logo)
                    if not os.path.exists(logo_path):
                        logo_path = None

                compra_data = {
                    'codigo': compra_completa.codigo,
                    'fecha': compra_completa.fecha.strftime('%Y-%m-%d'),
                    'proveedor_nombre': proveedor_compra.nombre if proveedor_compra else 'N/A',
                    'proveedor_rnc': proveedor_compra.rnc if proveedor_compra else 'N/A',
                    'empresa_nombre': empresa.nombrec if empresa else 'Mi Empresa',
                    'empresa_rnc': empresa.rnc if empresa else '',
                    'empresa_direccion': empresa.direccionc if empresa else '',
                    'empresa_logo_path': logo_path,
                    'condicion': compra_completa.condicion,
                    'comentario': compra_completa.comentario,
                    'subtotal': compra_completa.subtotal,
                    'descuento': compra_completa.descuento,
                    'itbis': compra_completa.itbis,
                    'total': compra_completa.total,
                    'detalles': []
                }

                detalles_compra = ComprasD.query.filter_by(compra_id=compra.id).all()
                for det in detalles_compra:
                    mercancia_detalle = Mercancia.query.get(det.mercancia_id)
                    compra_data['detalles'].append({
                        'mercancia_codigo': mercancia_detalle.codigo if mercancia_detalle else 'N/A',
                        'mercancia_nombre': mercancia_detalle.nombre if mercancia_detalle else 'N/A',
                        'cantidad': det.cantidad,
                        'precio': det.precio,
                        'importe': det.importe
                    })

                # Generar el PDF en memoria
                buffer = io.BytesIO()
                generate_compra_pdf(compra_data, buffer)
                buffer.seek(0)

                pdf_filename = f"compra_{compra.codigo}.pdf"
                pdf_path = os.path.join(app.root_path, 'static', 'pdfs', pdf_filename)

                # Asegurarse de que el directorio static/pdfs exista
                os.makedirs(os.path.dirname(pdf_path), exist_ok=True)

                with open(pdf_path, 'wb') as f:
                    f.write(buffer.getvalue())

                flash(f'Compra guardada correctamente. PDF generado: {pdf_filename}', 'success')
                return redirect(url_for('compras'))

            except Exception as e:
                flash(f'Error al generar PDF de la compra: {e}', 'warning')
                return redirect(url_for('compras'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar compra: {e}', 'danger')
        return redirect(url_for('compras'))

    return render_template('compras.html', page_title='Compras', form_name='compras', current_date=date.today())



# === API: Buscar compras ===
@app.route('/api/compras')
@login_required
def api_compras():
    q = (request.args.get('q') or '').strip()
    proveedor_id = request.args.get('proveedor_id')
    query = ComprasC.query.join(Proveedor, ComprasC.proveedor_id == Proveedor.id, isouter=True)

    if proveedor_id:
        query = query.filter(ComprasC.proveedor_id == proveedor_id)
    if q:
        like = f"%{q}%"
        query = query.filter(or_(
            ComprasC.codigo.ilike(like), 
            ComprasC.comentario.ilike(like),
            Proveedor.nombre.ilike(like)
        ))
    filas = query.order_by(ComprasC.fecha.desc(), ComprasC.codigo.desc()).limit(50).all()
    result = []
    for f in filas:
        prov = Proveedor.query.get(f.proveedor_id) if f.proveedor_id else None
        result.append({
            'id': f.id,
            'codigo': f.codigo,
            'fecha': f.fecha.isoformat() if f.fecha else None,
            'referencia': f.referencia,
            'condicion': f.condicion,
            'proveedor_id': f.proveedor_id,
            'proveedor_nombre': prov.nombre if prov else None,
            'proveedor_rnc': prov.rnc if prov else None,
            'comentario': f.comentario,
            'estado': f.estado,
            'subtotal': float(f.subtotal or 0),
            'itbis': float(f.itbis or 0),
            'descuento': float(f.descuento or 0),
            'total': float(f.total or 0),
            'detalles': [{
                'id': d.id,
                'mercancia_id': d.mercancia_id,
                'mercancia_codigo': d.mercancia.codigo if d.mercancia else None,
                'mercancia_nombre': d.mercancia.nombre if d.mercancia else None,
                'existencia': d.mercancia.existencia if d.mercancia else None,
                'cantidad': int(d.cantidad or 0),
                'precio': float(d.precio or 0),
                'costo': float(d.costo or 0),
                'importe': float(d.importe or 0),
            } for d in f.detalles]
        })
    return jsonify(result)

# === API: Obtener compra por id (incluye detalles) ===
@app.route('/api/compras/<int:id>')
@login_required
def api_compra(id):
    f = ComprasC.query.get_or_404(id)
    prov = Proveedor.query.get(f.proveedor_id) if f.proveedor_id else None
    detalles = ComprasD.query.filter_by(compra_id=f.id).all()
    det_out = []
    for d in detalles:
        m = Mercancia.query.get(d.mercancia_id)
        det_out.append({
            'id': d.id,
            'mercancia_id': d.mercancia_id,
            'mercancia_codigo': m.codigo if m else None,
            'mercancia_nombre': m.nombre if m else None,
            'existencia': m.existencia if m else None,
            'cantidad': int(d.cantidad or 0),
            'precio': float(d.precio or 0),
            'costo': float(d.costo or 0),
            'importe': float(d.importe or 0),
        })
    return jsonify({
        'id': f.id,
        'codigo': f.codigo,
        'fecha': f.fecha.isoformat() if f.fecha else None,
        'referencia': f.referencia,
        'condicion': f.condicion,
        'proveedor_id': f.proveedor_id,
        'proveedor_nombre': prov.nombre if prov else None,
        'proveedor_rnc': prov.rnc if prov else None,
        'comentario': f.comentario,
        'estado': f.estado,
        'subtotal': float(f.subtotal or 0),
        'itbis': float(f.itbis or 0),
        'descuento': float(f.descuento or 0),
        'total': float(f.total or 0),
        'detalles': det_out,
    })


# === API: Buscar ajustes ===
@app.route('/api/ajustes')
@login_required
def api_ajustes():
    q = (request.args.get('q') or '').strip()
    query = AjusteC.query
    if q:
        like = f"%{q}%"
        query = query.filter((AjusteC.codigo.ilike(like)) | (AjusteC.comentario.ilike(like)))
    ajustes = query.order_by(AjusteC.fecha.desc(), AjusteC.codigo.desc()).limit(50).all()
    return jsonify([
        {
            'id': a.id,
            'codigo': a.codigo,
            'fecha': a.fecha.isoformat() if a.fecha else None,
            'clase': a.clase,
            'comentario': a.comentario,
            'total': float(a.total) if a.total is not None else 0,
            'estado': a.estado,
        } for a in ajustes
    ])

# === API: Obtener ajuste por id (incluye detalles) ===
@app.route('/api/ajustes/<int:id>')
@login_required
def api_ajuste(id):
    a = AjusteC.query.get_or_404(id)
    detalles = AjusteD.query.filter_by(ajuste_id=a.id).all()
    return jsonify({
        'id': a.id,
        'codigo': a.codigo,
        'fecha': a.fecha.isoformat() if a.fecha else None,
        'clase': a.clase,
        'comentario': a.comentario,
        'total': float(a.total) if a.total is not None else 0,
        'estado': a.estado,
        'detalles': [
            {
                'id': d.id,
                'mercancia_id': d.mercancia_id,
                'mercancia_codigo': d.mercancia.codigo if d.mercancia else None,
                'mercancia_nombre': d.mercancia.nombre if d.mercancia else None,
                'existencia': d.mercancia.existencia if d.mercancia else None,
                'cantidad': d.cantidad,
                'costo': float(d.costo) if d.costo is not None else 0,
            } for d in detalles
        ]
    })

# === API: Buscar mercancías por nombre ===
@app.route('/api/mercancias')
@login_required
def api_mercancias():
    q = (request.args.get('q') or '').strip()
    query = Mercancia.query
    if q:
        query = query.filter(or_(
            Mercancia.nombre.ilike(f"%{q}%"),
            Mercancia.codigo.ilike(f"%{q}%")
        ))
    mercancias = query.order_by(Mercancia.nombre).limit(50).all()
    return jsonify([
        {
            'id': m.id,
            'codigo': m.codigo,
            'nombre': m.nombre,
            'precio': float(m.precio) if m.precio else 0,
            'existencia': m.existencia,
            'costo': float(m.costo) if m.costo else 0,
            'tipo': m.tipo,
            'clase_id': m.clase_id,
            'clase_nombre': m.clase.nombre if m.clase else None,
        } for m in mercancias
    ])

# === API: Obtener una mercancía por id ===
@app.route('/api/mercancias/<int:id>')
@login_required
def api_mercancia(id):
    m = Mercancia.query.get_or_404(id)
    return jsonify({
        'id': m.id,
        'codigo': m.codigo,
        'nombre': m.nombre,
        'precio': float(m.precio) if m.precio else 0,
        'existencia': m.existencia,
        'costo': float(m.costo) if m.costo else 0,
        'tipo': m.tipo,
        'clase_id': m.clase_id,
        'clase_nombre': m.clase.nombre if m.clase else None,
    })

# === TIPOS ===
@app.route('/tipos', methods=['GET','POST'])
@login_required
def tipos():
    if request.method == 'POST':
        tipo_id = request.form.get('id')
        nombre = request.form.get('nombre')
        clase = request.form.get('clase')
        
        if tipo_id:
            try:
                tipo = Tipo.query.get(int(tipo_id))
                if not tipo:
                    flash('Tipo no encontrado.', 'warning')
                    return redirect(url_for('tipos'))
                tipo.nombre = nombre
                tipo.clase = clase
                db.session.commit()
                flash('Tipo actualizado correctamente.', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error al actualizar tipo: {e}', 'danger')
            return redirect(url_for('tipos'))
        else:
            try:
                nuevo = Tipo(nombre=nombre, clase=clase)
                db.session.add(nuevo)
                db.session.commit()
                flash('Tipo guardado correctamente.', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error al guardar tipo: {e}', 'danger')
            return redirect(url_for('tipos'))

    return render_template('tipos.html', page_title='Tipos', form_name='tipos')

# === API: Buscar tipos por nombre o clase ===
@app.route('/api/tipos')
@login_required
def api_tipos():
    q = (request.args.get('q') or '').strip()
    clase = (request.args.get('clase') or '').strip()
    query = Tipo.query
    if q:
        query = query.filter(Tipo.nombre.ilike(f"%{q}%"))
    if clase:
        query = query.filter(Tipo.clase == clase)
    tipos = query.order_by(Tipo.clase, Tipo.nombre).limit(50).all()
    return jsonify([
        {
            'id': t.id,
            'nombre': t.nombre,
            'clase': t.clase,
        } for t in tipos
    ])

# === API: Obtener un tipo por id ===
@app.route('/api/tipos/<int:id>')
@login_required
def api_tipo(id):
    t = Tipo.query.get_or_404(id)
    return jsonify({
        'id': t.id,
        'nombre': t.nombre,
        'clase': t.clase,
    })

# === API: Obtener tipos de mercancía para selector ===
@app.route('/api/tipos/mercancia')
@login_required
def api_tipos_mercancia():
    tipos = Tipo.query.filter(Tipo.clase == 'mercancia').order_by(Tipo.nombre).all()
    return jsonify([
        {
            'id': t.id,
            'nombre': t.nombre,
        } for t in tipos
    ])

# Scaffold routes for other menu items (you can add more similarly)
@app.route('/comprobantes')
@login_required
def comprobantes():
    return render_template('form_page.html', page_title='Comprobantes', form_name='comprobantes')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('index.html')

@app.route('/reportes')
@login_required
def reportes():
    return render_template('form_page.html', page_title='Reportes', form_name='reportes')


# ReportLab imports for PDF generation
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors

@app.route('/mercancias/reporte_pdf')
@login_required
def mercancias_reporte_pdf():
    # Consulta: join con Tipo (clase) y ordenar por clase y nombre
    registros = (
        db.session.query(Mercancia, Tipo)
        .outerjoin(Tipo, Mercancia.clase_id == Tipo.id)
        .order_by(Tipo.nombre, Mercancia.nombre)
        .all()
    )

    # Agrupar por nombre de clase
    grupos = {}
    for merc, tipo in registros:
        nombre_clase = tipo.nombre if tipo and tipo.nombre else 'Sin clase'
        grupos.setdefault(nombre_clase, []).append(merc)

    # Crear PDF en memoria
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elementos = []

    elementos.append(Paragraph('Reporte de Mercancías por Clase', styles['Title']))
    elementos.append(Spacer(1, 12))

    # Construir tablas por grupo
    for clase, mercs in grupos.items():
        elementos.append(Paragraph(f'Clase: {clase}', styles['Heading2']))
        data = [['Código', 'Nombre', 'Tipo', 'Precio', 'Existencia', 'Costo']]
        for m in mercs:
            data.append([
                m.codigo or '',
                m.nombre or '',
                m.tipo or '',
                f"{m.precio:.2f}" if m.precio is not None else '0.00',
                str(m.existencia or 0),
                f"{m.costo:.2f}" if m.costo is not None else '0.00'
            ])
        tabla = Table(data, repeatRows=1)
        tabla.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0f0f0')),
            ('TEXTCOLOR', (0,0), (-1,0), colors.black),
            ('GRID', (0,0), (-1,-1), 0.25, colors.gray),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
            ('ALIGN', (3,1), (5,-1), 'RIGHT'),
            ('BOTTOMPADDING', (0,0), (-1,0), 6),
            ('TOPPADDING', (0,1), (-1,-1), 3),
        ]))
        elementos.append(tabla)
        elementos.append(Spacer(1, 18))

    doc.build(elementos)
    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name='mercancias_por_clase.pdf',
        mimetype='application/pdf'
    )

# === CREAR TABLAS DESDE LA WEB ===
@app.route('/configuracion/crear_tablas', methods=['POST'])
@login_required
def crear_tablas():
    try:
        db.create_all()

        # Sembrar datos iniciales en la tabla de secuencias
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
            db.session.execute(text("INSERT INTO secuencias (codigo, secuencia, clase) VALUES (:codigo, :secuencia, :clase) ON CONFLICT (clase) DO NOTHING;"), s)
        
        # Sembrar datos iniciales en la tabla 'empresa' si está vacía
        if db.session.query(Empresa).count() == 0:
            db.session.add(Empresa(id=1, nombrec='Nombre de tu Empresa'))

        db.session.commit()
        flash('¡Tablas creadas y datos iniciales sembrados con éxito!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al crear las tablas: {e}', 'danger')
    return redirect(url_for('configuracion'))

# === DATOS DE LA EMPRESA ===
@app.route('/empresa', methods=['GET', 'POST'])
@login_required
def datos_empresa():
    # Siempre trabajaremos con la empresa de ID=1
    empresa = Empresa.query.get_or_404(1)

    if request.method == 'POST':
        try:
            empresa.nombrec = request.form.get('nombrec')
            empresa.direccionc = request.form.get('direccionc')
            empresa.telefonos = request.form.get('telefonos')
            empresa.correo = request.form.get('correo')
            empresa.rnc = request.form.get('rnc')

            # Manejo de la subida del logo
            if 'logo' in request.files:
                file = request.files['logo']
                if file.filename != '':
                    # Asegurarse de que el directorio de subidas exista
                    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
                    # Borrar logo anterior si existe
                    if empresa.logo:
                        old_logo_path = os.path.join(app.config['UPLOAD_FOLDER'], empresa.logo)
                        if os.path.exists(old_logo_path):
                            os.remove(old_logo_path)
                    
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    empresa.logo = filename

            db.session.commit()
            # flash('Datos de la empresa actualizados correctamente.', 'success')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar los datos de la empresa: {e}', 'danger')
        return redirect(url_for('datos_empresa'))

    return render_template('empresa.html', page_title='Datos de la Empresa', empresa=empresa)

@app.route('/configuracion')
@login_required
def configuracion():
    return render_template(
        'configuracion.html',
        page_title='Configuración',
        form_name='configuracion',
        driver=cfg_driver,
        server=cfg_server,
        database=cfg_database,
        username=cfg_username,
        password=cfg_password,
    )

@app.route('/usuarios', methods=['GET','POST'])
@login_required
def usuarios():
    if request.method == 'POST':
        usr_id = request.form.get('id')
        username = request.form.get('username')
        fullname = request.form.get('fullname')
        photo_url = request.form.get('photo_url')
        password = request.form.get('password')
        
        if usr_id:
            try:
                u = User.query.get(int(usr_id))
                if not u:
                    flash('Usuario no encontrado.', 'warning')
                    return redirect(url_for('usuarios'))
                # Verificar colisión de username si cambió
                if username and username != u.username:
                    if User.query.filter_by(username=username).first():
                        flash('Nombre de usuario ya existe.', 'danger')
                        return redirect(url_for('usuarios'))
                    u.username = username
                u.fullname = fullname
                u.photo_url = photo_url
                if password:
                    u.set_password(password)
                db.session.commit()
                flash('Usuario actualizado correctamente.', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error al actualizar usuario: {e}', 'danger')
            return redirect(url_for('usuarios'))
        else:
            try:
                if not username:
                    flash('Usuario es requerido.', 'warning')
                    return redirect(url_for('usuarios'))
                if User.query.filter_by(username=username).first():
                    flash('Nombre de usuario ya existe.', 'danger')
                    return redirect(url_for('usuarios'))
                nuevo = User(username=username, fullname=fullname, photo_url=photo_url)
                if password:
                    nuevo.set_password(password)
                else:
                    # Permitir creación con clave vacía (no recomendado, pero según scaffold)
                    nuevo.password_hash = ''
                db.session.add(nuevo)
                db.session.commit()
                flash('Usuario guardado correctamente.', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error al guardar usuario: {e}', 'danger')
            return redirect(url_for('usuarios'))
    return render_template('usuarios.html', page_title='Usuarios', form_name='usuarios')

# === API: Buscar usuarios por username o nombre ===
@app.route('/api/usuarios')
@login_required
def api_usuarios():
    q = (request.args.get('q') or '').strip()
    query = User.query
    if q:
        like = f"%{q}%"
        query = query.filter((User.username.ilike(like)) | (User.fullname.ilike(like)))
    usuarios = query.order_by(User.username).limit(50).all()
    return jsonify([
        {
            'id': u.id,
            'username': u.username,
            'fullname': u.fullname,
            'photo_url': u.photo_url,
        } for u in usuarios
    ])

# === API: Obtener un usuario por id ===
@app.route('/api/usuarios/<int:id>')
@login_required
def api_usuario(id):
    u = User.query.get_or_404(id)
    return jsonify({
        'id': u.id,
        'username': u.username,
        'fullname': u.fullname,
        'photo_url': u.photo_url,
    })

# === API: Obtener tipos de gasto (soporta 'gasto' y 'general') ===
@app.route('/api/tipos/gasto')
@login_required
def api_tipos_gasto():
    tipos = Tipo.query.filter(Tipo.clase.in_(['gasto','general'])).order_by(Tipo.nombre).all()
    return jsonify([
        {
            'id': t.id,
            'nombre': t.nombre,
        } for t in tipos
    ])

# === GASTOS ===
@app.route('/gastos', methods=['GET','POST'])
@login_required
def gastos():
    if request.method == 'POST':
        gasto_id = request.form.get('id')
        codigo = request.form.get('codigo')
        fecha_str = request.form.get('fecha')
        descripcion = request.form.get('descripcion')
        monto = request.form.get('monto')
        documento = request.form.get('documento')
        clase_id = request.form.get('clase_id')

        # Parse fecha
        fecha = None
        try:
            if fecha_str:
                fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except Exception:
            fecha = None

        if gasto_id:
            try:
                g = Gasto.query.get(int(gasto_id))
                if not g:
                    flash('Gasto no encontrado.', 'warning')
                    return redirect(url_for('gastos'))
                g.codigo = codigo
                g.fecha = fecha
                g.descripcion = descripcion
                g.monto = float(monto) if monto else 0
                g.documento = documento
                g.clase_id = int(clase_id) if clase_id else None
                db.session.commit()
                flash('Gasto actualizado correctamente.', 'success')
            except Exception as e:
                db.session.rollback()
                flash(f'Error al actualizar gasto: {e}', 'danger')
            return redirect(url_for('gastos'))
        else:
            try:
                # Generar código automático usando la tabla 'secuencias' para clase 'gasto'
                auto_codigo = (codigo or '').strip()
                if not auto_codigo:
                    try:
                        db.session.execute(text("INSERT INTO secuencias (codigo, secuencia, clase) VALUES ('G', 1, 'gasto') ON CONFLICT (clase) DO NOTHING;"))
                    except Exception:
                        pass

                    row = db.session.execute(text("SELECT codigo, secuencia FROM secuencias WHERE clase = :clase FOR UPDATE"), {'clase': 'gasto'}).fetchone()
                    db.session.execute(text("UPDATE secuencias SET secuencia = secuencia + 1 WHERE clase = :clase"), {'clase': 'gasto'})
                    prefix = row[0] if row else 'G'
                    prev_seq = row[1] if row else 1
                    auto_codigo = f"{prefix}{prev_seq:06d}"

                nuevo = Gasto(
                    codigo=auto_codigo,
                    fecha=fecha,
                    descripcion=descripcion,
                    monto=float(monto) if monto else 0,
                    documento=documento,
                    clase_id=int(clase_id) if clase_id else None
                )
                db.session.add(nuevo)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                flash(f'Error al guardar gasto: {e}', 'danger')
            return redirect(url_for('gastos'))

    return render_template('gastos.html', page_title='Gastos', form_name='gastos')

# === API: Buscar gastos ===
@app.route('/api/gastos')
@login_required
def api_gastos():
    q = (request.args.get('q') or '').strip()
    query = Gasto.query
    if q:
        like = f"%{q}%"
        query = query.filter((Gasto.descripcion.ilike(like)) | (Gasto.codigo.ilike(like)))
    gastos = query.order_by(Gasto.fecha.desc(), Gasto.codigo).limit(50).all()
    return jsonify([
        {
            'id': g.id,
            'codigo': g.codigo,
            'fecha': g.fecha.isoformat() if g.fecha else None,
            'descripcion': g.descripcion,
            'monto': float(g.monto) if g.monto is not None else 0,
            'documento': g.documento,
            'clase_id': g.clase_id,
            'clase_nombre': g.clase.nombre if g.clase else None,
        } for g in gastos
    ])

# === API: Obtener un gasto por id ===
@app.route('/api/gastos/<int:id>')
@login_required
def api_gasto(id):
    g = Gasto.query.get_or_404(id)
    return jsonify({
        'id': g.id,
        'codigo': g.codigo,
        'fecha': g.fecha.isoformat() if g.fecha else None,
        'descripcion': g.descripcion,
        'monto': float(g.monto) if g.monto is not None else 0,
        'documento': g.documento,
        'clase_id': g.clase_id,
        'clase_nombre': g.clase.nombre if g.clase else None,
    })

@app.route('/api/gastos/por_fecha')
@login_required
def api_gastos_por_fecha():
    desde = request.args.get('desde')
    hasta = request.args.get('hasta')
    d = None
    h = None
    try:
        if desde:
            d = datetime.strptime(desde, '%Y-%m-%d').date()
        if hasta:
            h = datetime.strptime(hasta, '%Y-%m-%d').date()
    except Exception:
        d = None
        h = None
    query = Gasto.query
    if d:
        query = query.filter(Gasto.fecha >= d)
    if h:
        query = query.filter(Gasto.fecha <= h)
    gastos = query.order_by(Gasto.fecha.asc(), Gasto.codigo.asc()).all()
    result = []
    for g in gastos:
        result.append({
            'id': g.id,
            'codigo': g.codigo,
            'fecha': g.fecha.isoformat() if g.fecha else None,
            'descripcion': g.descripcion,
            'monto': float(g.monto) if g.monto is not None else None,
            'documento': g.documento,
            'clase': getattr(g.clase, 'nombre', None) if hasattr(g, 'clase') else None,
        })
    return jsonify(result)

@app.route('/gastos/reporte_pdf')
@login_required
def gastos_reporte_pdf():
    desde = request.args.get('desde')
    hasta = request.args.get('hasta')
    d = None
    h = None
    try:
        if desde:
            d = datetime.strptime(desde, '%Y-%m-%d').date()
        if hasta:
            h = datetime.strptime(hasta, '%Y-%m-%d').date()
    except Exception:
        d = None
        h = None

    query = Gasto.query
    if d:
        query = query.filter(Gasto.fecha >= d)
    if h:
        query = query.filter(Gasto.fecha <= h)
    gastos = query.order_by(Gasto.fecha.asc(), Gasto.codigo.asc()).all()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    title = Paragraph('Reporte de Gastos', styles['Title'])
    elements.append(title)
    rango_text = f"Rango: {desde or '—'} a {hasta or '—'}"
    elements.append(Paragraph(rango_text, styles['Normal']))
    elements.append(Spacer(1, 12))

    data = [['Código', 'Fecha', 'Descripción', 'Monto', 'Documento', 'Clase']]
    total = 0.0
    for g in gastos:
        fecha_str = g.fecha.strftime('%d/%m/%Y') if g.fecha else ''
        monto_val = float(g.monto) if g.monto is not None else 0.0
        total += monto_val
        data.append([
            g.codigo or '',
            fecha_str,
            g.descripcion or '',
            f"{monto_val:,.2f}",
            g.documento or '',
            getattr(g.clase, 'nombre', '') if hasattr(g, 'clase') else ''
        ])

    table = Table(data, repeatRows=1)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (3,1), (3,-1), 'RIGHT'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.gray),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Total: {total:,.2f}", styles['Heading4']))

    doc.build(elements)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name='gastos_reporte.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    # Este bloque es solo para desarrollo local.
    # En producción, se usará un servidor WSGI como Gunicorn.
    # El modo debug se deshabilita para producción.
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
