# -*- coding: utf-8 -*-
"""
AutoLux Kids - Simulador de compra de coches de lujo
=======================================================
Backend en Flask que expone una pequeña API REST para:
  - Listar los coches del "showroom" (catálogo).
  - Consultar el estado del jugador (saldo de LuxCoins y garaje).
  - Simular la compra de un coche (sin pagos reales, moneda ficticia).
  - Simular la venta de un coche (devuelve parte del valor).
  - Reiniciar la partida.

No se procesan pagos reales ni se guardan datos personales: todo vive
en la sesión de Flask (cookie firmada), pensado como un juego /
simulador educativo y divertido para niños y niñas.
"""

from flask import Flask, jsonify, render_template, request, session
import uuid
import time

app = Flask(__name__)

# Clave secreta para firmar la cookie de sesión.
# En un proyecto real, esto vendría de una variable de entorno.
app.secret_key = "autolux-kids-super-secreto-de-demostracion"

# Saldo inicial de "LuxCoins" (moneda ficticia) con el que empieza cada jugador.
SALDO_INICIAL = 5_000_000

# Porcentaje que se devuelve al "vender" un coche del garaje (simula depreciación,
# de forma sencilla y divertida, no realista al 100%).
PORCENTAJE_REVENTA = 0.7


# ---------------------------------------------------------------------------
# Catálogo de coches (showroom)
# ---------------------------------------------------------------------------
# Los modelos son ficticios (inspirados en el estilo de marcas icónicas del
# mundo del motor) para poder jugar libremente sin representar productos
# reales concretos. El campo "color" se usa en el frontend para pintar la
# silueta SVG del coche.
COCHES = [
    {
        "id": 1,
        "marca": "Ferrari",
        "modelo": "Fenice GT",
        "apodo": "El Fénix Veloz",
        "precio": 950_000,
        "potencia_hp": 720,
        "velocidad_max": 340,
        "aceleracion": 2.9,
        "plazas": 2,
        "rareza": "Legendaria",
        "color": "#E63946",
        "color_secundario": "#FFD166",
        "spoiler": True,
        "descripcion": "Un bólido rojo llameante que ruge como un dragón "
                        "y acelera más rápido que tu grito favorito en la "
                        "montaña rusa.",
    },
    {
        "id": 2,
        "marca": "Lamborghini",
        "modelo": "Toro Fulmine",
        "apodo": "El Toro Rayo",
        "precio": 980_000,
        "potencia_hp": 730,
        "velocidad_max": 350,
        "aceleracion": 2.8,
        "plazas": 2,
        "rareza": "Legendaria",
        "color": "#FFD500",
        "color_secundario": "#111111",
        "spoiler": True,
        "descripcion": "Bajo y anguloso como un rayo dibujado por un "
                        "superhéroe, este toro embiste el asfalto con "
                        "puertas que se abren hacia el cielo.",
    },
    {
        "id": 3,
        "marca": "Porsche",
        "modelo": "Spectra Turbo",
        "apodo": "El Fantasma Veloz",
        "precio": 480_000,
        "potencia_hp": 580,
        "velocidad_max": 320,
        "aceleracion": 3.2,
        "plazas": 4,
        "rareza": "Rara",
        "color": "#1D8FE1",
        "color_secundario": "#F1FAEE",
        "spoiler": True,
        "descripcion": "Elegante, azul como el cielo despejado y tan "
                        "silencioso que parece flotar sobre la carretera.",
    },
    {
        "id": 4,
        "marca": "Bugatti",
        "modelo": "Corona Diamante",
        "apodo": "La Joya Real",
        "precio": 2_600_000,
        "potencia_hp": 1500,
        "velocidad_max": 420,
        "aceleracion": 2.3,
        "plazas": 2,
        "rareza": "Mítica",
        "color": "#3A0CA3",
        "color_secundario": "#D4AF37",
        "spoiler": False,
        "descripcion": "El coche más raro y brillante del showroom: cuesta "
                        "una fortuna en LuxCoins y vuela como un cohete "
                        "con corbata de gala.",
    },
    {
        "id": 5,
        "marca": "McLaren",
        "modelo": "Nébula Naranja",
        "apodo": "El Cometa",
        "precio": 610_000,
        "potencia_hp": 650,
        "velocidad_max": 330,
        "aceleracion": 2.9,
        "plazas": 2,
        "rareza": "Rara",
        "color": "#FF7B00",
        "color_secundario": "#111111",
        "spoiler": True,
        "descripcion": "Naranja brillante, ligero como una pluma y con un "
                        "diseño futurista que parece salido de una nave "
                        "espacial.",
    },
    {
        "id": 6,
        "marca": "Aston Martin",
        "modelo": "Elegancia Verde",
        "apodo": "El Agente Secreto",
        "precio": 540_000,
        "potencia_hp": 520,
        "velocidad_max": 310,
        "aceleracion": 3.5,
        "plazas": 2,
        "rareza": "Rara",
        "color": "#2D6A4F",
        "color_secundario": "#D4AF37",
        "spoiler": False,
        "descripcion": "Tan elegante que podría ir a una fiesta de gala, "
                        "pero tan rápido que llegaría antes de que suene "
                        "la invitación.",
    },
    {
        "id": 7,
        "marca": "Rolls-Royce",
        "modelo": "Majestad Perlada",
        "apodo": "El Palacio con Ruedas",
        "precio": 720_000,
        "potencia_hp": 460,
        "velocidad_max": 250,
        "aceleracion": 4.8,
        "plazas": 4,
        "rareza": "Rara",
        "color": "#F7F3E9",
        "color_secundario": "#D4AF37",
        "spoiler": False,
        "descripcion": "Blanco perla y suave como una nube: es el coche "
                        "favorito de quienes prefieren viajar como "
                        "auténtica realeza.",
    },
    {
        "id": 8,
        "marca": "Bentley",
        "modelo": "Zafiro Real",
        "apodo": "El Duque Azul",
        "precio": 560_000,
        "potencia_hp": 500,
        "velocidad_max": 290,
        "aceleracion": 4.0,
        "plazas": 4,
        "rareza": "Común",
        "color": "#14213D",
        "color_secundario": "#D4AF37",
        "spoiler": False,
        "descripcion": "Azul profundo como el océano a medianoche, con un "
                        "interior tan cómodo que parece un sofá con "
                        "motor.",
    },
]


def buscar_coche(coche_id):
    """Devuelve el diccionario del coche con el id indicado, o None."""
    return next((c for c in COCHES if c["id"] == coche_id), None)


def obtener_estado():
    """Inicializa (si hace falta) y devuelve el estado de la sesión actual."""
    if "saldo" not in session:
        session["saldo"] = SALDO_INICIAL
    if "garaje" not in session:
        session["garaje"] = []
    return session["saldo"], session["garaje"]


# ---------------------------------------------------------------------------
# Rutas de vistas
# ---------------------------------------------------------------------------
@app.route("/")
def index():
    """Página principal: el showroom de coches de lujo."""
    obtener_estado()  # Se asegura de que la sesión tenga saldo y garaje.
    return render_template("index.html")


# ---------------------------------------------------------------------------
# API REST
# ---------------------------------------------------------------------------
@app.route("/api/coches", methods=["GET"])
def api_coches():
    """Devuelve el catálogo completo de coches del showroom."""
    return jsonify(COCHES)


@app.route("/api/estado", methods=["GET"])
def api_estado():
    """Devuelve el saldo actual y el garaje del jugador."""
    saldo, garaje = obtener_estado()
    return jsonify({"saldo": saldo, "garaje": garaje, "saldo_inicial": SALDO_INICIAL})


@app.route("/api/comprar", methods=["POST"])
def api_comprar():
    """
    Simula la compra de un coche.
    Espera un JSON: { "coche_id": int, "comprador": str }
    """
    saldo, garaje = obtener_estado()
    datos = request.get_json(silent=True) or {}

    coche_id = datos.get("coche_id")
    comprador = (datos.get("comprador") or "Piloto misterioso").strip()[:40]

    coche = buscar_coche(coche_id)
    if coche is None:
        return jsonify({"ok": False, "error": "Ese coche no existe en el showroom."}), 404

    if saldo < coche["precio"]:
        return jsonify({
            "ok": False,
            "error": "¡Saldo insuficiente! Necesitas más LuxCoins para este coche.",
        }), 400

    # Se crea el "recibo" / pedido simulado.
    pedido = {
        "pedido_id": str(uuid.uuid4())[:8].upper(),
        "coche": coche,
        "comprador": comprador,
        "fecha": time.strftime("%d/%m/%Y %H:%M"),
    }

    saldo -= coche["precio"]
    garaje.append(pedido)

    session["saldo"] = saldo
    session["garaje"] = garaje
    session.modified = True

    return jsonify({"ok": True, "pedido": pedido, "saldo": saldo})


@app.route("/api/vender", methods=["POST"])
def api_vender():
    """
    Simula la venta de un coche que ya está en el garaje.
    Espera un JSON: { "pedido_id": str }
    Devuelve al jugador un porcentaje del precio original (diversión, no realismo).
    """
    saldo, garaje = obtener_estado()
    datos = request.get_json(silent=True) or {}
    pedido_id = datos.get("pedido_id")

    pedido = next((p for p in garaje if p["pedido_id"] == pedido_id), None)
    if pedido is None:
        return jsonify({"ok": False, "error": "No se encontró ese coche en tu garaje."}), 404

    reembolso = int(pedido["coche"]["precio"] * PORCENTAJE_REVENTA)
    garaje = [p for p in garaje if p["pedido_id"] != pedido_id]
    saldo += reembolso

    session["saldo"] = saldo
    session["garaje"] = garaje
    session.modified = True

    return jsonify({"ok": True, "reembolso": reembolso, "saldo": saldo})


@app.route("/api/reiniciar", methods=["POST"])
def api_reiniciar():
    """Reinicia la partida: restaura el saldo inicial y vacía el garaje."""
    session["saldo"] = SALDO_INICIAL
    session["garaje"] = []
    session.modified = True
    return jsonify({"ok": True, "saldo": SALDO_INICIAL, "garaje": []})


if __name__ == "__main__":
    # debug=True solo para desarrollo local.
    app.run(debug=True)
