from app import db

class Camion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(64), nullable=False)
    lat = db.Column(db.Float)
    lon = db.Column(db.Float)
    ordenes = db.relationship("Factura", backref="camion", lazy=True)


class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(128), nullable=True)
    telefono = db.Column(db.String(20), nullable=True)

    # Relación con órdenes o facturas (por ejemplo, órdenes)
    # facturas = db.relationship("Factura", backref="cliente", lazy=True)             


'''

class OrdenServicio(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    direccion = db.Column(db.String(256), nullable=False)
    estado = db.Column(db.String(32), nullable=False, default="Pendiente")  # Pendiente, En proceso, Completada
    costo = db.Column(db.Float, nullable=False)
    camion_id =  db.Column(db.Integer, db.ForeignKey("camion.id"))
    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    chofer_id = db.Column(db.Integer, db.ForeignKey('chofer.id'), nullable=True)
    # chofer = db.relationship('Chofer', backref='ordenes')

    @property
    def costo_calculado(self):
        return sum(f.monto_total or 0 for f in self.facturas)
    
    @property
    def todas_facturas_pagadas(self):
        return all((f.monto_pagado or 0) >= (f.monto_total or 0) for f in self.facturas)


'''



class Factura(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), unique=True, nullable=False)
    direccion = db.Column(db.String(256), nullable=False)
    fecha = db.Column(db.Date, nullable=False)
    due_date = db.Column(db.Date, nullable=True)
    monto_total = db.Column(db.Float, nullable=False)
    monto_pagado = db.Column(db.Float, nullable=False, default=0.0)
    estado = db.Column(db.String(50), default='Pendiente')  # 👈 nuevo campo

    cliente_id = db.Column(db.Integer, db.ForeignKey('cliente.id'), nullable=False)
    # En Factura:
    camion_id = db.Column(db.Integer, db.ForeignKey('camion.id'), nullable=True)
    chofer_id = db.Column(db.Integer, db.ForeignKey('chofer.id'), nullable=True)
    # orden_id = db.Column(db.Integer, db.ForeignKey('orden_servicio.id'), nullable=True)

    cliente = db.relationship("Cliente", backref="facturas")
    # orden = db.relationship("OrdenServicio", backref="factura")    
    # orden = db.relationship("OrdenServicio", backref="facturas")

    items = db.relationship("FacturaItem", backref="factura", lazy=True, cascade="all, delete-orphan")

    @property
    def monto_total_calculado(self):
        return sum(item.total for item in self.items)
    



    
class FacturaItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    factura_id = db.Column(db.Integer, db.ForeignKey('factura.id'), nullable=False)

    item = db.Column(db.String(128), nullable=False)         # Nombre corto
    descripcion = db.Column(db.String(256), nullable=True)
    precio_unitario = db.Column(db.Float, nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)

    @property
    def total(self):
        return self.precio_unitario * self.cantidad    
    
class Chofer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(64), nullable=False)
    apellidos = db.Column(db.String(64), nullable=False)
    telefono = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(128), nullable=True)
    ordenes = db.relationship("Factura", backref="chofer", lazy=True)

    def __repr__(self):
        return f"<Chofer {self.nombre} {self.apellidos}>"
    

    