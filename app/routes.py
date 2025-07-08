from flask import render_template, request, redirect, url_for, jsonify, make_response, current_app
from weasyprint import HTML
from app import app, db
from app.models import Camion,  Cliente, Factura, FacturaItem, Chofer   # OrdenServicio,
from datetime import datetime
from email.message import EmailMessage
import smtplib
from flask import flash
from flask_mail import Message
from app import mail
import os
import re

from datetime import datetime
from flask import render_template
from io import BytesIO
from pdf2image import convert_from_bytes
from flask import send_file
import io

# from weasyprint import HTML




@app.route('/back')
def index_back():
    # ordenes = OrdenServicio.query.all()
    camiones = Camion.query.all()
    clientes = Cliente.query.all()
    facturas = Factura.query.all()
    choferes = Chofer.query.all()
    return render_template("index.html",  camiones=camiones, clientes=clientes, facturas=facturas, choferes=choferes)
    # return render_template("index.html", ordenes=ordenes, camiones=camiones, clientes=clientes, facturas=facturas, choferes=choferes)
    

@app.route('/')
def index():
    return render_template('index.html')



@app.route('/facturas/dia/<fecha>')
def facturas_por_dia(fecha):
    from datetime import datetime
    fecha_dt = datetime.strptime(fecha, '%Y-%m-%d').date()
    facturas = Factura.query.filter_by(fecha=fecha_dt).all()
    clientes = Cliente.query.order_by(Cliente.nombre).all()
    choferes = Chofer.query.all()
    return render_template('facturas_por_dia.html', facturas=facturas, fecha=fecha_dt, clientes=clientes, choferes=choferes)




def actualizar_estado_orden(orden):
    if orden.todas_facturas_pagadas and orden.estado != 'Completada':
        orden.estado = 'Completada'
        db.session.commit()



@app.route('/factura/<int:id>/actualizar_monto_pagado', methods=['POST'])
def actualizar_monto_pagado(id):
    factura = Factura.query.get_or_404(id)
    try:
        nuevo_monto = float(request.form.get('monto_pagado', 0))
        monto_anterior = factura.monto_pagado or 0

        factura.monto_pagado = nuevo_monto
        db.session.commit()

        # Si la factura está asociada a una orden, verificar si todas están pagadas
        if factura.orden:
            if all((f.monto_pagado or 0) >= (f.monto_total or 0) for f in factura.orden.facturas):
                factura.orden.estado = 'Completada'
                db.session.commit()

        flash(f'Monto pagado actualizado. ${monto_anterior:.2f} -> ${nuevo_monto:.2f}', 'success')

    except Exception as e:
        db.session.rollback()
        flash('Error al actualizar monto.', 'danger')

    return redirect(url_for('listar_facturas'))




@app.route("/camion/nuevo", methods=["GET", "POST"])
def nuevo_camion():
    if request.method == "POST":
        nombre = request.form["nombre"]
        lat = float(request.form["lat"])
        lon = float(request.form["lon"])
        camion = Camion(nombre=nombre, lat=lat, lon=lon)
        db.session.add(camion)
        db.session.commit()
        flash("Camion agregado", "success")
        return redirect(url_for("index"))
    return render_template("nuevo_camion.html")


@app.route("/camion/<int:id>/editar", methods=["GET", "POST"])
def editar_camion(id):
    camion = Camion.query.get_or_404(id)
    if request.method == "POST":
        camion.nombre = request.form["nombre"]
        camion.lat = float(request.form["lat"])
        camion.lon = float(request.form["lon"])
        db.session.commit()
        return redirect(url_for("index"))
    return render_template("editar_camion.html", camion=camion)

@app.route("/camion/<int:id>/eliminar", methods=["POST"])
def eliminar_camion(id):
    camion = Camion.query.get_or_404(id)
    db.session.delete(camion)
    db.session.commit()
    flash("Camion eliminado", "warning")
    return redirect(url_for("index"))

@app.route("/cliente/nuevo", methods=["GET", "POST"])
def nuevo_cliente():
    if request.method == "POST":
        nombre = request.form["nombre"]
        email = request.form["email"]
        telefono = request.form["telefono"]
        cliente = Cliente(nombre=nombre, email=email, telefono=telefono)
        db.session.add(cliente)
        db.session.commit()
        flash("Cliente agregado", "success")
        return redirect(url_for("index"))
    return render_template("nuevo_cliente.html")

@app.route("/cliente/<int:id>/editar", methods=["GET", "POST"])
def editar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    if request.method == "POST":
        cliente.nombre = request.form["nombre"]
        cliente.email = request.form["email"]
        cliente.telefono = request.form["telefono"]
        db.session.commit()
        flash("Cliente actualizado", "success")
        return redirect(url_for("index"))
    return render_template("editar_cliente.html", cliente=cliente)

@app.route("/cliente/<int:id>/eliminar", methods=["POST"])
def eliminar_cliente(id):
    cliente = Cliente.query.get_or_404(id)
    db.session.delete(cliente)
    db.session.commit()
    flash("Cliente eliminado", "warning")
    return redirect(url_for("index"))





@app.route('/factura/nueva', methods=['GET', 'POST'])
def nueva_factura():
    if request.method == 'POST':
        numero = request.form.get('numero')
        fecha = datetime.strptime(request.form.get('fecha'), '%Y-%m-%d')
        due_date = request.form.get('due_date')
        due_date = datetime.strptime(due_date, '%Y-%m-%d') if due_date else None
        direccion = request.form.get('direccion')
        # estado = request.form.get('estado')
        if monto_pagado >= costo:
            estado = "pagada"
       
        else:
            estado = "pendiente"
        costo = float(request.form.get('costo') or 0)
        cliente_id = int(request.form.get('cliente_id'))
        camion_id = request.form.get('camion_id')
        camion_id = int(camion_id) if camion_id else None
        chofer_id = request.form.get('chofer_id')
        chofer_id = int(chofer_id) if chofer_id else None
        monto_pagado = float(request.form.get('monto_pagado') or 0)
        
        
        
        factura = Factura(
            numero=numero,
            fecha=fecha,
            due_date=due_date,
            direccion=direccion,
            estado=estado,
            costo=costo,
            cliente_id=cliente_id,
            camion_id=camion_id,
            chofer_id=chofer_id,
            monto_pagado=monto_pagado
        )
        db.session.add(factura)
        db.session.commit()
        
        return redirect(url_for('ver_factura', factura_id=factura.id))
    
    clientes = Cliente.query.all()
    camiones = Camion.query.all()
    choferes = Chofer.query.all()
    return render_template('nueva_factura.html', clientes=clientes, camiones=camiones, choferes=choferes)


from datetime import datetime

@app.route('/api/factura/<int:id>/editar', methods=['POST'])
def editar_factura_api(id):
    data = request.get_json()
    if not data:
        return jsonify({"error": "No se recibió data"}), 400

    factura = Factura.query.get_or_404(id)

    try:
        factura.numero = data.get('numero', factura.numero)
        factura.direccion = data.get('direccion', factura.direccion)
        # factura.fecha = datetime.strptime(data.get('fecha', str(factura.fecha)), '%Y-%m-%d').date()
        fecha_str = data.get('fecha')
        if fecha_str:
            factura.fecha = datetime.strptime(fecha_str.strip(), '%Y-%m-%d').date()

        # ✅ Parsear due_date si existe
        due_date_str = data.get('due_date')
        if due_date_str:
            factura.due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()

        factura.monto_pagado = float(data.get('monto_pagado', factura.monto_pagado))

        # ✅ Actualiza cliente y chofer
        factura.cliente_id = int(data.get('cliente_id', factura.cliente_id))
        factura.chofer_id = int(data.get('chofer_id')) if data.get('chofer_id') else None

        # Eliminar items actuales
        FacturaItem.query.filter_by(factura_id=factura.id).delete()

        total = 0
        for item_data in data.get('items', []):
            precio_unitario = float(item_data.get('precio_unitario', 0))
            cantidad = int(item_data.get('cantidad', 0))
            total_item = precio_unitario * cantidad

            item = FacturaItem(
                factura_id=factura.id,
                item=item_data.get('item'),
                descripcion=item_data.get('descripcion'),
                precio_unitario=precio_unitario,
                cantidad=cantidad,
            )
            db.session.add(item)
            total += total_item

        factura.monto_total = total

        # ✅ Actualiza estado
        factura.estado = "pagada" if factura.monto_pagado >= total else "pendiente"

        db.session.commit()

        return jsonify({
            "mensaje": "Factura actualizada correctamente",
            "factura_id": factura.id,
            "estado": factura.estado,
            "cliente_id": factura.cliente_id,
            "chofer_id": factura.chofer_id,
            "due_date": factura.due_date.isoformat() if factura.due_date else None  # opcional
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error al actualizar", "detalle": str(e)}), 500





@app.route("/factura/<int:id>/editar", methods=["GET", "POST"])
def editar_factura(id):
    factura = Factura.query.get_or_404(id)
    if request.method == "POST":
        factura.fecha = datetime.strptime(request.form["fecha"], "%Y-%m-%d").date()
        factura.monto_total = float(request.form["monto_total"])
        factura.cliente_id = int(request.form["cliente_id"])
        orden_id = request.form["orden_id"]
        factura.orden_id = int(orden_id) if orden_id else None
        db.session.commit()
        return redirect(url_for("index"))

    clientes = Cliente.query.all()
    # ordenes = OrdenServicio.query.all()
    return render_template("editar_factura.html", factura=factura, clientes=clientes)

@app.route("/factura/<int:id>/eliminar", methods=["POST"])
def eliminar_factura(id):
    factura = Factura.query.get_or_404(id)
    db.session.delete(factura)
    db.session.commit()
    return redirect(url_for("index"))

@app.route("/clientes")
def listar_clientes():
    clientes = Cliente.query.all()
    return render_template("clientes.html", clientes=clientes)

@app.route("/camiones")
def listar_camiones():
    camiones = Camion.query.all()
    return render_template("camiones.html", camiones=camiones)

@app.route("/facturas")
def listar_facturas():
    facturas = Factura.query.all()
    return render_template("facturas.html", facturas=facturas)


@app.route('/factura/<int:id>/pdf')
def imprimir_factura_pdf(id):
    factura = Factura.query.get_or_404(id)

    # Renderizamos la plantilla HTML con los datos de la factura
    html_out = render_template('factura_pdf.html', factura=factura)

    # Convertimos el HTML a PDF
    pdf = HTML(string=html_out).write_pdf()

    # Enviamos el PDF como respuesta
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=factura_{id}.pdf'
    return response



@app.route("/factura/<int:id>/enviar")
def enviar_factura_email(id):
    factura = Factura.query.get_or_404(id)

    if not factura.cliente.email:
        flash("Este cliente no tiene correo electrónico registrado.", "warning")
        return redirect(url_for("listar_facturas"))

    # Generar HTML del PDF (usa tu template factura_pdf.html)
    html = render_template("factura_pdf.html", factura=factura)
    pdf = HTML(string=html).write_pdf()

    msg = Message(subject=f'Factura #{factura.id}',
                  recipients=[factura.cliente.email],
                  body=f'Adjunto se encuentra la factura #{factura.id}.')

    # Adjuntar el PDF: el contenido debe ser bytes, y Flask-Mail lo espera así
    msg.attach(f'factura_{factura.id}.pdf', 'application/pdf', pdf)

    try:
        mail.send(msg)
        flash("Factura enviada exitosamente al cliente.", "success")
    except Exception as e:
        flash(f"Error al enviar correo: {e}", "danger")

    return redirect(url_for("listar_facturas"))


# Listar choferes
@app.route("/choferes")
def listar_choferes():
    choferes = Chofer.query.all()
    return render_template("choferes.html", choferes=choferes)

# Crear nuevo chofer
@app.route("/choferes/nuevo", methods=["GET", "POST"])
def nuevo_chofer():
    if request.method == "POST":
        chofer = Chofer(
            nombre=request.form["nombre"],
            apellidos=request.form["apellidos"],
            telefono=request.form.get("telefono"),
            email=request.form.get("email"),
        )
        db.session.add(chofer)
        db.session.commit()
        flash("Chofer agregado", "success")
        return redirect(url_for("listar_choferes"))
    return render_template("chofer_form.html", chofer=None)

# Editar chofer
@app.route("/choferes/editar/<int:id>", methods=["GET", "POST"])
def editar_chofer(id):
    chofer = Chofer.query.get_or_404(id)
    if request.method == "POST":
        chofer.nombre = request.form["nombre"]
        chofer.apellidos = request.form["apellidos"]
        chofer.telefono = request.form.get("telefono")
        chofer.email = request.form.get("email")
        db.session.commit()
        flash("Chofer actualizado", "success")
        return redirect(url_for("listar_choferes"))
    return render_template("chofer_form.html", chofer=chofer)

# Eliminar chofer
@app.route("/choferes/eliminar/<int:id>", methods=["POST"])
def eliminar_chofer(id):
    chofer = Chofer.query.get_or_404(id)
    db.session.delete(chofer)
    db.session.commit()
    flash("Chofer eliminado", "warning")
    return redirect(url_for("listar_choferes"))






@app.route('/orden/test', methods=['GET', 'POST'])
def nueva_orden_test():
    if request.method == 'POST':
        data = request.form
        items = []
        for desc, price, qty in zip(data.getlist('desc[]'), data.getlist('unit_price[]'), data.getlist('qty[]')):
            items.append({'desc': desc, 'unit_price': float(price), 'qty': int(qty)})

        invoice_data = {
            'direccion': data['direccion'],
            'estado': data['estado'],
            'cliente': data['cliente'],
            'chofer': data['chofer'],
            'camion': data['camion'],
            'costo_estimado': float(data['costo_estimado']),
            'numero_factura': data['numero_factura'],
            'fecha': data['fecha'],
            'vencimiento': data['vencimiento'],
            'email_cliente': data['email_cliente'],
            'items': items,
            'subtotal': float(data['subtotal']),
            'pagado': float(data['pagado']),
            'balance': float(data['balance'])
        }

        # save_invoice(invoice_data)
        return redirect('/')
    return render_template('invoice.html')


def generar_numero_factura_por_direccion(direccion):
    # Extraer el primer número de la dirección
    match = re.search(r'\b\d+\b', direccion)
    if not match:
        return None  # o un valor por defecto

    base_numero = match.group(0)

    # Buscar todos los números que empiezan con base_numero
    existentes = (
        db.session.query(Factura.numero)
        .filter(Factura.numero.like(f"{base_numero}%"))
        .all()
    )
    numeros_existentes = [num for (num,) in existentes]

    if base_numero not in numeros_existentes:
        return base_numero
    else:
        letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        sufijos = [num[len(base_numero):] for num in numeros_existentes if len(num) > len(base_numero)]
        sufijos = [s for s in sufijos if s.isalpha()]
        # Buscar la primera letra disponible
        for letra in letras:
            if letra not in sufijos:
                return base_numero + letra
        # Si se agotaron las letras, devolver con sufijo numérico o error
        return base_numero + "Z1"  # o manejar error según prefieras


@app.route('/api/factura/nueva', methods=['PUT'])
def api_crear_factura():
    data = request.get_json()
    print("Recibido:", data)

    if not data:
        return jsonify({"error": "No data received"}), 400

    numero = data.get('numero')
    direccion = data.get('direccion')
    fecha_str = data.get('fecha')
    due_date_str = data.get('due_date')  # ✅
    items_data = data.get('items', [])

    try:
        cliente_id = int(data.get('cliente_id'))
        chofer_id = int(data.get('chofer_id')) if data.get('chofer_id') else None  # ✅
    except (ValueError, TypeError):
        return jsonify({"error": "cliente_id o chofer_id inválido"}), 400

    if not numero or not direccion or not fecha_str:
        return jsonify({"error": "Faltan campos obligatorios"}), 400

    try:
        fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
    except ValueError:
        return jsonify({"error": "Fecha inválida"}), 400

    try:
        due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date() if due_date_str else None  # ✅
    except ValueError:
        return jsonify({"error": "Due Date inválida"}), 400

    factura = Factura(
        numero=numero,
        direccion=direccion,
        fecha=fecha,
        due_date=due_date,           # ✅ asignar due_date
        cliente_id=cliente_id,
        chofer_id=chofer_id,         # ✅ asignar chofer_id
        monto_pagado=0.0,
        monto_total=0.0
    )

    db.session.add(factura)
    db.session.flush()

    total_factura = 0.0
    for item in items_data:
        precio_unitario = float(item.get('precio_unitario', 0))
        cantidad = int(item.get('cantidad', 0))
        total = precio_unitario * cantidad

        factura_item = FacturaItem(
            factura_id=factura.id,
            item=item.get('item'),
            descripcion=item.get('descripcion'),
            precio_unitario=precio_unitario,
            cantidad=cantidad,
        )
        db.session.add(factura_item)
        total_factura += total

    factura.monto_total = total_factura

    try:
        db.session.commit()
        return jsonify({
            "mensaje": "Factura creada correctamente",
            "factura_id": factura.id,
            "chofer_id": factura.chofer_id,
            "due_date": factura.due_date.isoformat() if factura.due_date else None
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Error guardando factura", "detalle": str(e)}), 500


@app.route('/api/facturas/numeros_por_dia')
def facturas_numeros_por_dia():
    facturas = Factura.query.all()
    eventos = []
    for f in facturas:
        eventos.append({
            "title": f.numero,
            "start": f.fecha.isoformat(),
            "allDay": True,
            "estado": f.estado.lower() if f.estado else "desconocido"
        })
    return jsonify(eventos)

@app.route('/api/factura/existe_numero/<string:numero>')
def verificar_numero_factura(numero):
    existe = Factura.query.filter_by(numero=numero).first() is not None
    return jsonify({"existe": existe})

'''

@app.route('/factura/<int:id>/pdf')
def factura_pdf(id):
    factura = Factura.query.get_or_404(id)
    html = render_template('factura_pdf.html', factura=factura)
    pdf_file = BytesIO()
    HTML(string=html).write_pdf(pdf_file)
    pdf_file.seek(0)

    response = make_response(pdf_file.read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=factura_{id}.pdf'
    return response
'''



@app.route('/factura/<int:id>/pdf')
def generar_factura_pdf(id):
    factura = Factura.query.get_or_404(id)
    html = render_template('factura_1_pdf.html', factura=factura)
    
    # Convertir HTML a PDF en memoria
    pdf_file = HTML(string=html).write_pdf()

    response = make_response(pdf_file)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=factura_{factura.numero}.pdf'
    return response

'''
@app.route('/factura/pdf/<int:factura_id>')
def servir_pdf(factura_id):
    filename = f"factura_{factura_id}.pdf"
    return send_from_directory('static/facturas_pdfs', filename)


'''

@app.route('/factura/<int:id>/imagen')
def factura_imagen(id):
    factura = Factura.query.get_or_404(id)
    # Renderizamos el PDF primero igual que antes
    rendered = render_template('factura_pdf.html', factura=factura, cliente=factura.cliente, items=factura.items, chofer=factura.chofer)
    pdf_bytes = HTML(string=rendered).write_pdf()

    # Convertir PDF bytes a imagen (lista de PIL images)
    images = convert_from_bytes(pdf_bytes, dpi=150)
    # Tomamos la primera página para enviar (puedes adaptar si hay más páginas)
    image_io = io.BytesIO()
    images[0].save(image_io, format='PNG')
    image_io.seek(0)

    return send_file(image_io, mimetype='image/png', download_name=f'factura_{factura.numero}.png')