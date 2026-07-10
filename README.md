# 🏎️ AutoLux Kids — Simulador de compra de coches de lujo

Un showroom virtual, elegante y divertido, donde puedes explorar
superdeportivos de fantasía, leer su ficha técnica y "comprarlos" con
una moneda ficticia (**LuxCoins 🪙**). No se realiza ningún pago real
ni se piden datos personales sensibles: es 100% un juego de simulación.

## ✨ Qué incluye

- **Backend en Flask** (`app.py`) con una pequeña API REST:
  - `GET /api/coches` — catálogo del showroom.
  - `GET /api/estado` — saldo y garaje del jugador (guardado en sesión).
  - `POST /api/comprar` — simula la compra de un coche.
  - `POST /api/vender` — simula la venta de un coche del garaje.
  - `POST /api/reiniciar` — reinicia la partida.
- **Frontend en HTML + CSS + JavaScript vanilla** (sin frameworks):
  - Tarjetas de coche con silueta SVG dibujada por código (sin usar
    logotipos ni imágenes de marcas reales).
  - Ficha técnica tipo "carnet de piloto" con barras de estadísticas
    animadas (potencia, velocidad máxima, aceleración, plazas).
  - Flujo de compra con confirmación de nombre, recibo y confeti 🎉.
  - Sección "Mi Garaje" para ver y vender los coches comprados.
  - Diseño de lujo (negro + dorado) con toques lúdicos y coloridos
    pensado para que niños y niñas disfruten explorando.

## 🚀 Cómo ejecutarlo

1. Crea un entorno virtual (opcional pero recomendado):
   ```bash
   python -m venv venv
   source venv/bin/activate      # En Windows: venv\Scripts\activate
   ```

2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Ejecuta el servidor:
   ```bash
   python app.py
   ```

4. Abre tu navegador en:
   ```
   http://127.0.0.1:5000
   ```

## 📂 Estructura del proyecto

```
autolux_kids/
├── app.py                  # Backend Flask + API + catálogo de coches
├── requirements.txt
├── README.md
├── templates/
│   └── index.html          # Estructura de la página (showroom, modales, garaje)
└── static/
    ├── css/
    │   └── style.css       # Estilos: paleta de lujo + animaciones
    └── js/
        └── script.js       # Lógica de UI, API fetch, SVG, confeti
```

## 🧒 Notas para un uso seguro con niños

- Los coches son **modelos ficticios** inspirados en el mundo del motor;
  no se reproducen logotipos ni imágenes reales de ninguna marca.
- La moneda del juego (**LuxCoins**) es completamente inventada: no hay
  conexión con tarjetas, bancos ni pagos reales.
- El botón **↺ Reiniciar** permite empezar de nuevo en cualquier momento.

## 🎨 Personalización rápida

- Para añadir más coches, edita la lista `COCHES` en `app.py`.
- Para cambiar la paleta de colores, ajusta las variables `:root` al
  inicio de `static/css/style.css`.
- El saldo inicial y el porcentaje de reventa se controlan con las
  constantes `SALDO_INICIAL` y `PORCENTAJE_REVENTA` en `app.py`.
