# -*- coding: utf-8 -*-
"""
AutoMarket Premium
Simulador de compra de coches - Concesionaria de lujo
Backend: Flask + SQLite
Ejecutar con: python app.py
"""

import os
import sqlite3
import random
import string
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, flash, g, jsonify
)

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")

app = Flask(__name__)
app.secret_key = "automarket-premium-secret-key-2026-change-in-production"

ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

IVA = 0.18  # impuesto simulado 18%

# ---------------------------------------------------------------------------
# BASE DE DATOS
# ---------------------------------------------------------------------------

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Crea las tablas y carga datos de ejemplo si la base no existe."""
    first_run = not os.path.exists(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS vehicles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            year INTEGER NOT NULL,
            price REAL NOT NULL,
            mileage INTEGER NOT NULL,
            fuel TEXT NOT NULL,
            transmission TEXT NOT NULL,
            color TEXT NOT NULL,
            condition_status TEXT NOT NULL DEFAULT 'Usado',
            status TEXT NOT NULL DEFAULT 'Disponible',
            engine TEXT,
            power TEXT,
            consumption TEXT,
            description TEXT,
            features TEXT,
            image TEXT,
            created_at TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_number TEXT NOT NULL,
            order_date TEXT NOT NULL,
            vehicle_id INTEGER,
            vehicle_brand TEXT,
            vehicle_model TEXT,
            vehicle_year INTEGER,
            vehicle_price REAL,
            first_name TEXT,
            last_name TEXT,
            dni TEXT,
            phone TEXT,
            email TEXT,
            address TEXT,
            down_payment REAL,
            installments INTEGER,
            payment_method TEXT,
            monthly_payment REAL,
            interest REAL,
            total_payment REAL
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            message TEXT,
            created_at TEXT
        )
    """)

    conn.commit()

    if first_run:
        seed_vehicles(cur)
        conn.commit()

    conn.close()


def seed_vehicles(cur):
    """Inserta 30 vehiculos de ejemplo de distintas marcas."""
    colors = ["Negro", "Blanco", "Gris", "Azul", "Rojo", "Plata"]
    fuels = ["Gasolina", "Diesel", "Hibrido", "Electrico"]
    transmissions = ["Automatica", "Manual"]

    vehicles = [
        # brand, model, year, price, mileage, fuel, transmission, color, condition, engine, power, consumption
        ("Toyota", "Corolla", 2023, 21500, 12000, "Gasolina", "Automatica", "Blanco", "Usado", "1.8L 4 cil.", "140 HP", "6.5 L/100km"),
        ("Toyota", "Camry", 2024, 28900, 5000, "Hibrido", "Automatica", "Gris", "Nuevo", "2.5L Hibrido", "208 HP", "4.8 L/100km"),
        ("Toyota", "RAV4", 2022, 27500, 30000, "Hibrido", "Automatica", "Azul", "Usado", "2.5L Hibrido", "219 HP", "5.7 L/100km"),
        ("BMW", "Serie 3", 2023, 42500, 8000, "Gasolina", "Automatica", "Negro", "Usado", "2.0L Turbo", "255 HP", "7.1 L/100km"),
        ("BMW", "X5", 2022, 61900, 25000, "Diesel", "Automatica", "Gris", "Usado", "3.0L Turbo Diesel", "265 HP", "8.3 L/100km"),
        ("BMW", "M4", 2024, 89900, 3000, "Gasolina", "Automatica", "Azul", "Nuevo", "3.0L Biturbo", "473 HP", "10.2 L/100km"),
        ("Mercedes-Benz", "Clase C", 2023, 45900, 10000, "Gasolina", "Automatica", "Plata", "Usado", "2.0L Turbo", "255 HP", "7.3 L/100km"),
        ("Mercedes-Benz", "GLE", 2022, 68500, 22000, "Diesel", "Automatica", "Negro", "Usado", "3.0L Turbo Diesel", "330 HP", "8.9 L/100km"),
        ("Mercedes-Benz", "Clase S", 2024, 112000, 2000, "Hibrido", "Automatica", "Negro", "Nuevo", "3.0L Hibrido", "429 HP", "8.0 L/100km"),
        ("Audi", "A4", 2023, 39900, 15000, "Gasolina", "Automatica", "Blanco", "Usado", "2.0L TFSI", "190 HP", "6.9 L/100km"),
        ("Audi", "Q7", 2022, 64900, 28000, "Diesel", "Automatica", "Gris", "Usado", "3.0L TDI", "286 HP", "7.8 L/100km"),
        ("Audi", "RS7", 2024, 128000, 1500, "Gasolina", "Automatica", "Rojo", "Nuevo", "4.0L V8 Biturbo", "591 HP", "11.5 L/100km"),
        ("Honda", "Civic", 2023, 23900, 11000, "Gasolina", "Manual", "Rojo", "Usado", "1.5L Turbo", "180 HP", "6.7 L/100km"),
        ("Honda", "CR-V", 2022, 29500, 19000, "Hibrido", "Automatica", "Azul", "Usado", "2.0L Hibrido", "212 HP", "5.5 L/100km"),
        ("Nissan", "Sentra", 2023, 20900, 14000, "Gasolina", "Automatica", "Gris", "Usado", "1.8L 4 cil.", "149 HP", "6.9 L/100km"),
        ("Nissan", "Altima", 2022, 24500, 21000, "Gasolina", "Automatica", "Negro", "Usado", "2.5L 4 cil.", "188 HP", "7.2 L/100km"),
        ("Mazda", "Mazda3", 2023, 22900, 9000, "Gasolina", "Automatica", "Rojo", "Usado", "2.0L Skyactiv", "155 HP", "6.6 L/100km"),
        ("Mazda", "CX-5", 2024, 31900, 4000, "Gasolina", "Automatica", "Blanco", "Nuevo", "2.5L Skyactiv", "187 HP", "7.4 L/100km"),
        ("Hyundai", "Elantra", 2023, 21500, 13000, "Gasolina", "Automatica", "Plata", "Usado", "2.0L 4 cil.", "147 HP", "6.8 L/100km"),
        ("Hyundai", "Tucson", 2022, 27900, 24000, "Hibrido", "Automatica", "Azul", "Usado", "1.6L Hibrido", "226 HP", "5.9 L/100km"),
        ("Kia", "Sportage", 2023, 28500, 16000, "Gasolina", "Automatica", "Gris", "Usado", "2.5L 4 cil.", "187 HP", "8.0 L/100km"),
        ("Kia", "K5", 2024, 26900, 6000, "Gasolina", "Automatica", "Negro", "Nuevo", "1.6L Turbo", "180 HP", "7.1 L/100km"),
        ("Ford", "Mustang", 2023, 42900, 12000, "Gasolina", "Manual", "Rojo", "Usado", "5.0L V8", "450 HP", "12.5 L/100km"),
        ("Ford", "Explorer", 2022, 38900, 27000, "Gasolina", "Automatica", "Negro", "Usado", "2.3L Turbo", "300 HP", "9.8 L/100km"),
        ("Chevrolet", "Camaro", 2023, 44900, 9500, "Gasolina", "Automatica", "Azul", "Usado", "6.2L V8", "455 HP", "12.9 L/100km"),
        ("Chevrolet", "Tahoe", 2022, 55900, 20000, "Gasolina", "Automatica", "Blanco", "Usado", "5.3L V8", "355 HP", "13.5 L/100km"),
        ("Volkswagen", "Golf GTI", 2023, 32900, 10500, "Gasolina", "Manual", "Blanco", "Usado", "2.0L Turbo", "241 HP", "7.6 L/100km"),
        ("Volkswagen", "Tiguan", 2024, 33900, 3500, "Gasolina", "Automatica", "Gris", "Nuevo", "2.0L TSI", "184 HP", "7.9 L/100km"),
        ("Lexus", "ES 300h", 2023, 47900, 8500, "Hibrido", "Automatica", "Negro", "Usado", "2.5L Hibrido", "215 HP", "5.0 L/100km"),
        ("Lexus", "RX 350", 2024, 52900, 4000, "Gasolina", "Automatica", "Plata", "Nuevo", "3.5L V6", "275 HP", "9.5 L/100km"),
        ("Porsche", "911 Carrera", 2024, 132000, 1000, "Gasolina", "Automatica", "Rojo", "Nuevo", "3.0L Twin-Turbo", "379 HP", "10.5 L/100km"),
        ("Porsche", "Cayenne", 2022, 89900, 18000, "Gasolina", "Automatica", "Negro", "Usado", "3.0L V6 Turbo", "335 HP", "10.9 L/100km"),
        ("Ferrari", "Roma", 2023, 245000, 2500, "Gasolina", "Automatica", "Rojo", "Usado", "3.9L V8 Biturbo", "612 HP", "13.8 L/100km"),
        ("Lamborghini", "Huracan", 2024, 289000, 800, "Gasolina", "Automatica", "Azul", "Nuevo", "5.2L V10", "630 HP", "14.5 L/100km"),
    ]

    features_pool = [
        "Aire acondicionado", "Bluetooth", "Camara de reversa", "Sensores de estacionamiento",
        "Techo panoramico", "Asientos de cuero", "Sistema de navegacion", "Control crucero adaptativo",
        "Llantas de aleacion", "Faros LED", "Apple CarPlay / Android Auto", "Sistema de sonido premium",
        "Frenado automatico de emergencia", "Asientos calefaccionados"
    ]

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for v in vehicles:
        (brand, model, year, price, mileage, fuel, transmission,
         color, condition, engine, power, consumption) = v

        feats = random.sample(features_pool, 6)
        description = (
            f"El {brand} {model} {year} combina elegancia, tecnologia y rendimiento. "
            f"Un vehiculo ideal para quienes buscan confort, seguridad y estilo en cada trayecto."
        )
        image_seed = f"{brand}-{model}".replace(" ", "-")
        image = f"https://placehold.co/640x420/1a1a2e/f5f5f5?text={brand.replace(' ', '+')}+{model.replace(' ', '+')}"

        cur.execute("""
            INSERT INTO vehicles
            (brand, model, year, price, mileage, fuel, transmission, color,
             condition_status, status, engine, power, consumption, description,
             features, image, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (brand, model, year, price, mileage, fuel, transmission, color,
              condition, "Disponible", engine, power, consumption, description,
              "|".join(feats), image, now))


# ---------------------------------------------------------------------------
# HELPERS
# ---------------------------------------------------------------------------

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("is_admin"):
            flash("Debes iniciar sesion para acceder al panel de administrador.", "error")
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated


def get_cart_ids():
    return session.get("cart", [])


def get_favorite_ids():
    return session.get("favorites", [])


def get_compare_ids():
    return session.get("compare", [])


def fetch_vehicles_by_ids(ids):
    if not ids:
        return []
    db = get_db()
    placeholders = ",".join("?" * len(ids))
    rows = db.execute(
        f"SELECT * FROM vehicles WHERE id IN ({placeholders})", ids
    ).fetchall()
    # preservar orden
    by_id = {row["id"]: row for row in rows}
    return [by_id[i] for i in ids if i in by_id]


def generate_order_number():
    letters = "".join(random.choices(string.ascii_uppercase, k=3))
    digits = "".join(random.choices(string.digits, k=6))
    return f"AM-{letters}{digits}"


@app.context_processor
def inject_globals():
    return {
        "cart_count": len(get_cart_ids()),
        "favorites_count": len(get_favorite_ids()),
        "compare_count": len(get_compare_ids()),
        "is_admin": session.get("is_admin", False),
        "current_year": datetime.now().year,
    }


# ---------------------------------------------------------------------------
# RUTAS PUBLICAS
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    db = get_db()
    featured = db.execute(
        "SELECT * FROM vehicles WHERE status = 'Disponible' ORDER BY price DESC LIMIT 6"
    ).fetchall()
    brands = db.execute(
        "SELECT brand, COUNT(*) as total FROM vehicles GROUP BY brand ORDER BY total DESC LIMIT 8"
    ).fetchall()
    total_vehicles = db.execute("SELECT COUNT(*) as c FROM vehicles").fetchone()["c"]
    total_sold = db.execute("SELECT COUNT(*) as c FROM vehicles WHERE status = 'Vendido'").fetchone()["c"]
    total_brands = db.execute("SELECT COUNT(DISTINCT brand) as c FROM vehicles").fetchone()["c"]
    return render_template(
        "index.html",
        featured=featured,
        brands=brands,
        stats={
            "vehicles": total_vehicles,
            "sold": total_sold,
            "brands": total_brands,
            "clients": 1280,
        },
    )


@app.route("/catalogo")
def catalog():
    db = get_db()

    search = request.args.get("q", "").strip()
    brand = request.args.get("brand", "")
    fuel = request.args.get("fuel", "")
    transmission = request.args.get("transmission", "")
    color = request.args.get("color", "")
    min_price = request.args.get("min_price", "")
    max_price = request.args.get("max_price", "")
    min_year = request.args.get("min_year", "")
    max_mileage = request.args.get("max_mileage", "")
    sort = request.args.get("sort", "")
    page = int(request.args.get("page", 1))
    per_page = 9

    query = "SELECT * FROM vehicles WHERE 1=1"
    params = []

    if search:
        query += " AND (brand LIKE ? OR model LIKE ?)"
        params += [f"%{search}%", f"%{search}%"]
    if brand:
        query += " AND brand = ?"
        params.append(brand)
    if fuel:
        query += " AND fuel = ?"
        params.append(fuel)
    if transmission:
        query += " AND transmission = ?"
        params.append(transmission)
    if color:
        query += " AND color = ?"
        params.append(color)
    if min_price:
        query += " AND price >= ?"
        params.append(float(min_price))
    if max_price:
        query += " AND price <= ?"
        params.append(float(max_price))
    if min_year:
        query += " AND year >= ?"
        params.append(int(min_year))
    if max_mileage:
        query += " AND mileage <= ?"
        params.append(int(max_mileage))

    if sort == "price_asc":
        query += " ORDER BY price ASC"
    elif sort == "price_desc":
        query += " ORDER BY price DESC"
    elif sort == "year_asc":
        query += " ORDER BY year ASC"
    elif sort == "year_desc":
        query += " ORDER BY year DESC"
    elif sort == "brand_asc":
        query += " ORDER BY brand ASC"
    else:
        query += " ORDER BY id DESC"

    all_results = db.execute(query, params).fetchall()
    total = len(all_results)
    total_pages = max(1, (total + per_page - 1) // per_page)
    page = max(1, min(page, total_pages))
    start = (page - 1) * per_page
    results = all_results[start:start + per_page]

    brands = [r["brand"] for r in db.execute("SELECT DISTINCT brand FROM vehicles ORDER BY brand").fetchall()]
    colors = [r["color"] for r in db.execute("SELECT DISTINCT color FROM vehicles ORDER BY color").fetchall()]

    return render_template(
        "catalog.html",
        vehicles=results,
        brands=brands,
        colors=colors,
        total=total,
        page=page,
        total_pages=total_pages,
        filters=request.args,
    )


@app.route("/vehiculo/<int:vehicle_id>")
def vehicle_detail(vehicle_id):
    db = get_db()
    vehicle = db.execute("SELECT * FROM vehicles WHERE id = ?", (vehicle_id,)).fetchone()
    if not vehicle:
        flash("El vehiculo solicitado no existe.", "error")
        return redirect(url_for("catalog"))
    related = db.execute(
        "SELECT * FROM vehicles WHERE brand = ? AND id != ? LIMIT 4",
        (vehicle["brand"], vehicle_id),
    ).fetchall()
    return render_template("vehicle_detail.html", vehicle=vehicle, related=related)


# --- Carrito ---

@app.route("/carrito")
def cart():
    ids = get_cart_ids()
    vehicles = fetch_vehicles_by_ids(ids)
    subtotal = sum(v["price"] for v in vehicles)
    taxes = subtotal * IVA
    total = subtotal + taxes
    return render_template("cart.html", vehicles=vehicles, subtotal=subtotal, taxes=taxes, total=total)


@app.route("/carrito/agregar/<int:vehicle_id>")
def cart_add(vehicle_id):
    cart_ids = get_cart_ids()
    if vehicle_id not in cart_ids:
        cart_ids.append(vehicle_id)
        session["cart"] = cart_ids
        flash("Vehiculo agregado al carrito.", "success")
    else:
        flash("Este vehiculo ya esta en tu carrito.", "info")
    return redirect(request.referrer or url_for("catalog"))


@app.route("/carrito/eliminar/<int:vehicle_id>")
def cart_remove(vehicle_id):
    cart_ids = get_cart_ids()
    if vehicle_id in cart_ids:
        cart_ids.remove(vehicle_id)
        session["cart"] = cart_ids
        flash("Vehiculo eliminado del carrito.", "info")
    return redirect(url_for("cart"))


@app.route("/carrito/vaciar")
def cart_clear():
    session["cart"] = []
    flash("Carrito vaciado.", "info")
    return redirect(url_for("cart"))


# --- Favoritos ---

@app.route("/favoritos")
def favorites():
    ids = get_favorite_ids()
    vehicles = fetch_vehicles_by_ids(ids)
    return render_template("favorites.html", vehicles=vehicles)


@app.route("/favoritos/agregar/<int:vehicle_id>")
def favorites_add(vehicle_id):
    fav_ids = get_favorite_ids()
    if vehicle_id not in fav_ids:
        fav_ids.append(vehicle_id)
        session["favorites"] = fav_ids
        flash("Agregado a favoritos.", "success")
    else:
        flash("Ya esta en tus favoritos.", "info")
    return redirect(request.referrer or url_for("catalog"))


@app.route("/favoritos/eliminar/<int:vehicle_id>")
def favorites_remove(vehicle_id):
    fav_ids = get_favorite_ids()
    if vehicle_id in fav_ids:
        fav_ids.remove(vehicle_id)
        session["favorites"] = fav_ids
        flash("Eliminado de favoritos.", "info")
    return redirect(request.referrer or url_for("favorites"))


# --- Comparador ---

@app.route("/comparar")
def compare():
    ids = get_compare_ids()
    vehicles = fetch_vehicles_by_ids(ids)
    return render_template("compare.html", vehicles=vehicles)


@app.route("/comparar/agregar/<int:vehicle_id>")
def compare_add(vehicle_id):
    comp_ids = get_compare_ids()
    if vehicle_id in comp_ids:
        flash("Este vehiculo ya esta en el comparador.", "info")
    elif len(comp_ids) >= 4:
        flash("Solo puedes comparar hasta 4 vehiculos. Elimina uno primero.", "error")
    else:
        comp_ids.append(vehicle_id)
        session["compare"] = comp_ids
        flash("Vehiculo agregado al comparador.", "success")
    return redirect(request.referrer or url_for("catalog"))


@app.route("/comparar/eliminar/<int:vehicle_id>")
def compare_remove(vehicle_id):
    comp_ids = get_compare_ids()
    if vehicle_id in comp_ids:
        comp_ids.remove(vehicle_id)
        session["compare"] = comp_ids
    return redirect(url_for("compare"))


# --- Financiamiento / Compra ---

@app.route("/financiamiento/<int:vehicle_id>", methods=["GET", "POST"])
def finance(vehicle_id):
    db = get_db()
    vehicle = db.execute("SELECT * FROM vehicles WHERE id = ?", (vehicle_id,)).fetchone()
    if not vehicle:
        flash("El vehiculo solicitado no existe.", "error")
        return redirect(url_for("catalog"))

    if request.method == "POST":
        first_name = request.form.get("first_name", "").strip()
        last_name = request.form.get("last_name", "").strip()
        dni = request.form.get("dni", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        address = request.form.get("address", "").strip()
        down_payment = float(request.form.get("down_payment", 0) or 0)
        installments = int(request.form.get("installments", 12) or 12)
        payment_method = request.form.get("payment_method", "Tarjeta de credito")

        errors = []
        if not first_name or not last_name:
            errors.append("El nombre y apellido son obligatorios.")
        if not dni or len(dni) < 5:
            errors.append("Ingresa un DNI valido.")
        if not phone:
            errors.append("El telefono es obligatorio.")
        if "@" not in email:
            errors.append("Ingresa un correo electronico valido.")
        if not address:
            errors.append("La direccion es obligatoria.")
        if down_payment < 0 or down_payment >= vehicle["price"]:
            errors.append("La inicial debe ser menor al precio del vehiculo.")
        if installments not in (12, 24, 36, 48, 60):
            errors.append("Selecciona un numero de cuotas valido.")

        if errors:
            for e in errors:
                flash(e, "error")
            return render_template("finance.html", vehicle=vehicle, form=request.form)

        # Calculo de financiamiento (interes simple anual del 12%)
        annual_rate = 0.12
        monthly_rate = annual_rate / 12
        principal = vehicle["price"] - down_payment

        if monthly_rate > 0:
            monthly_payment = (
                principal * monthly_rate * (1 + monthly_rate) ** installments
            ) / ((1 + monthly_rate) ** installments - 1)
        else:
            monthly_payment = principal / installments

        total_payment = monthly_payment * installments
        interest = total_payment - principal

        order_number = generate_order_number()
        order_date = datetime.now().strftime("%d/%m/%Y %H:%M")

        db.execute("""
            INSERT INTO orders (order_number, order_date, vehicle_id, vehicle_brand,
                vehicle_model, vehicle_year, vehicle_price, first_name, last_name, dni,
                phone, email, address, down_payment, installments, payment_method,
                monthly_payment, interest, total_payment)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (order_number, order_date, vehicle_id, vehicle["brand"], vehicle["model"],
              vehicle["year"], vehicle["price"], first_name, last_name, dni, phone,
              email, address, down_payment, installments, payment_method,
              round(monthly_payment, 2), round(interest, 2), round(total_payment, 2)))
        db.commit()

        order_id = db.execute("SELECT last_insert_rowid() as id").fetchone()["id"]

        # Marcar vehiculo como vendido
        db.execute("UPDATE vehicles SET status = 'Vendido' WHERE id = ?", (vehicle_id,))
        db.commit()

        flash("Compra realizada con exito. Aqui tienes tu factura.", "success")
        return redirect(url_for("invoice", order_id=order_id))

    return render_template("finance.html", vehicle=vehicle, form={})


@app.route("/factura/<int:order_id>")
def invoice(order_id):
    db = get_db()
    order = db.execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if not order:
        flash("La factura solicitada no existe.", "error")
        return redirect(url_for("index"))
    return render_template("invoice.html", order=order)


# --- Contacto / Acerca de ---

@app.route("/contacto", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        message = request.form.get("message", "").strip()

        if not name or "@" not in email or not message:
            flash("Por favor completa todos los campos correctamente.", "error")
        else:
            db = get_db()
            db.execute(
                "INSERT INTO contacts (name, email, message, created_at) VALUES (?, ?, ?, ?)",
                (name, email, message, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            )
            db.commit()
            flash("Tu mensaje ha sido enviado. Nos pondremos en contacto pronto.", "success")
            return redirect(url_for("contact"))
    return render_template("contact.html")


@app.route("/acerca-de")
def about():
    return render_template("about.html")


# ---------------------------------------------------------------------------
# PANEL DE ADMINISTRADOR
# ---------------------------------------------------------------------------

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["is_admin"] = True
            flash("Bienvenido al panel de administrador.", "success")
            return redirect(url_for("admin_dashboard"))
        flash("Usuario o contrasena incorrectos.", "error")
    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    flash("Sesion cerrada correctamente.", "info")
    return redirect(url_for("admin_login"))


@app.route("/admin")
@login_required
def admin_dashboard():
    db = get_db()
    total_vehicles = db.execute("SELECT COUNT(*) as c FROM vehicles").fetchone()["c"]
    available = db.execute("SELECT COUNT(*) as c FROM vehicles WHERE status='Disponible'").fetchone()["c"]
    sold = db.execute("SELECT COUNT(*) as c FROM vehicles WHERE status='Vendido'").fetchone()["c"]
    total_orders = db.execute("SELECT COUNT(*) as c FROM orders").fetchone()["c"]
    revenue = db.execute("SELECT COALESCE(SUM(vehicle_price),0) as s FROM orders").fetchone()["s"]
    by_brand = db.execute(
        "SELECT brand, COUNT(*) as total FROM vehicles GROUP BY brand ORDER BY total DESC"
    ).fetchall()
    recent_orders = db.execute(
        "SELECT * FROM orders ORDER BY id DESC LIMIT 5"
    ).fetchall()
    vehicles = db.execute("SELECT * FROM vehicles ORDER BY id DESC").fetchall()

    return render_template(
        "admin_dashboard.html",
        stats={
            "total": total_vehicles,
            "available": available,
            "sold": sold,
            "orders": total_orders,
            "revenue": revenue,
        },
        by_brand=by_brand,
        recent_orders=recent_orders,
        vehicles=vehicles,
    )


@app.route("/admin/vehiculo/nuevo", methods=["GET", "POST"])
@login_required
def admin_vehicle_new():
    if request.method == "POST":
        data = request.form
        image = data.get("image") or (
            f"https://placehold.co/640x420/1a1a2e/f5f5f5?text="
            f"{data.get('brand','Auto').replace(' ', '+')}+{data.get('model','').replace(' ', '+')}"
        )
        db = get_db()
        db.execute("""
            INSERT INTO vehicles (brand, model, year, price, mileage, fuel, transmission,
                color, condition_status, status, engine, power, consumption, description,
                features, image, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            data.get("brand"), data.get("model"), int(data.get("year")),
            float(data.get("price")), int(data.get("mileage")), data.get("fuel"),
            data.get("transmission"), data.get("color"), data.get("condition_status"),
            data.get("status", "Disponible"), data.get("engine"), data.get("power"),
            data.get("consumption"), data.get("description"), data.get("features"),
            image, datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        ))
        db.commit()
        flash("Vehiculo agregado correctamente.", "success")
        return redirect(url_for("admin_dashboard"))
    return render_template("admin_vehicle_form.html", vehicle=None)


@app.route("/admin/vehiculo/editar/<int:vehicle_id>", methods=["GET", "POST"])
@login_required
def admin_vehicle_edit(vehicle_id):
    db = get_db()
    vehicle = db.execute("SELECT * FROM vehicles WHERE id = ?", (vehicle_id,)).fetchone()
    if not vehicle:
        flash("Vehiculo no encontrado.", "error")
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        data = request.form
        db.execute("""
            UPDATE vehicles SET brand=?, model=?, year=?, price=?, mileage=?, fuel=?,
                transmission=?, color=?, condition_status=?, status=?, engine=?, power=?,
                consumption=?, description=?, features=?, image=?
            WHERE id = ?
        """, (
            data.get("brand"), data.get("model"), int(data.get("year")),
            float(data.get("price")), int(data.get("mileage")), data.get("fuel"),
            data.get("transmission"), data.get("color"), data.get("condition_status"),
            data.get("status"), data.get("engine"), data.get("power"),
            data.get("consumption"), data.get("description"), data.get("features"),
            data.get("image"), vehicle_id,
        ))
        db.commit()
        flash("Vehiculo actualizado correctamente.", "success")
        return redirect(url_for("admin_dashboard"))

    return render_template("admin_vehicle_form.html", vehicle=vehicle)


@app.route("/admin/vehiculo/eliminar/<int:vehicle_id>", methods=["POST"])
@login_required
def admin_vehicle_delete(vehicle_id):
    db = get_db()
    db.execute("DELETE FROM vehicles WHERE id = ?", (vehicle_id,))
    db.commit()
    flash("Vehiculo eliminado correctamente.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/vehiculo/vendido/<int:vehicle_id>", methods=["POST"])
@login_required
def admin_vehicle_toggle_sold(vehicle_id):
    db = get_db()
    vehicle = db.execute("SELECT * FROM vehicles WHERE id = ?", (vehicle_id,)).fetchone()
    if vehicle:
        new_status = "Vendido" if vehicle["status"] == "Disponible" else "Disponible"
        db.execute("UPDATE vehicles SET status = ? WHERE id = ?", (new_status, vehicle_id))
        db.commit()
        flash(f"Vehiculo marcado como {new_status}.", "success")
    return redirect(url_for("admin_dashboard"))


# ---------------------------------------------------------------------------
# API AUXILIAR (busqueda en tiempo real)
# ---------------------------------------------------------------------------

@app.route("/api/buscar")
def api_search():
    q = request.args.get("q", "").strip()
    db = get_db()
    if not q:
        return jsonify([])
    rows = db.execute(
        "SELECT id, brand, model, year, price, image FROM vehicles "
        "WHERE brand LIKE ? OR model LIKE ? LIMIT 8",
        (f"%{q}%", f"%{q}%"),
    ).fetchall()
    return jsonify([dict(r) for r in rows])


# ---------------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
