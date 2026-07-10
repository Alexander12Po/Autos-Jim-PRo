# AutoMarket Premium

Simulador completo de compra de vehiculos con apariencia de concesionaria de lujo.
Backend en Flask, base de datos SQLite, frontend en HTML5 + CSS3 + JavaScript puro.

## Caracteristicas

- Catalogo con filtros (marca, precio, año, combustible, transmision, color, kilometraje), buscador en tiempo real, ordenamiento y paginacion.
- Pagina de detalle de vehiculo con galeria, especificaciones y equipamiento.
- Comparador de hasta 4 vehiculos.
- Carrito de compras con calculo de subtotal, impuestos y total.
- Favoritos guardados en sesion.
- Simulador de financiamiento con calculo automatico de cuota mensual, intereses y total, generando una factura imprimible.
- Panel de administrador protegido (usuario/contraseña) para agregar, editar, eliminar y marcar vehiculos como vendidos, con estadisticas.
- Modo oscuro, notificaciones tipo toast, loader animado, boton "volver arriba", validaciones de formularios y mensajes flash.
- Base de datos SQLite generada automaticamente con 30+ vehiculos de ejemplo de marcas como Toyota, BMW, Mercedes-Benz, Audi, Honda, Nissan, Mazda, Hyundai, Kia, Ford, Chevrolet, Volkswagen, Lexus, Porsche, Ferrari y Lamborghini.

## Requisitos

- Python 3.9 o superior

## Instalacion y ejecucion

```bash
# 1. Entra a la carpeta del proyecto
cd automarket

# 2. (Opcional) crea un entorno virtual
python -m venv venv
source venv/bin/activate   # En Windows: venv\Scripts\activate

# 3. Instala las dependencias
pip install -r requirements.txt

# 4. Ejecuta la aplicacion
python app.py
```

La aplicacion estara disponible en **http://127.0.0.1:5000**

La base de datos `database.db` se crea automaticamente la primera vez que se ejecuta `app.py`, junto con 30+ vehiculos de ejemplo.

## Acceso al panel de administrador

- URL: `http://127.0.0.1:5000/admin/login`
- Usuario: `admin`
- Contraseña: `admin123`

> Nota: cambia estas credenciales en `app.py` (variables `ADMIN_USERNAME` y `ADMIN_PASSWORD`) antes de usar el proyecto en produccion.

## Estructura del proyecto

```
automarket/
├── app.py                     # Backend Flask (rutas, logica, base de datos)
├── requirements.txt           # Dependencias del proyecto
├── database.db                # Base de datos SQLite (se crea automaticamente)
├── README.md
├── templates/                 # Plantillas Jinja2 (HTML)
│   ├── base.html
│   ├── index.html
│   ├── catalog.html
│   ├── vehicle_detail.html
│   ├── compare.html
│   ├── cart.html
│   ├── favorites.html
│   ├── finance.html
│   ├── invoice.html
│   ├── admin_login.html
│   ├── admin_dashboard.html
│   ├── admin_vehicle_form.html
│   ├── contact.html
│   └── about.html
└── static/
    ├── css/style.css          # Estilos premium (modo claro/oscuro, responsive)
    ├── js/main.js              # Interactividad, modo oscuro, toasts, loader
    └── img/                    # Carpeta para imagenes adicionales
```

## Desplegar en Render

1. Sube este proyecto a un repositorio de GitHub (o GitLab).
2. Entra a [render.com](https://render.com) y crea una cuenta gratuita.
3. Click en **New +** → **Web Service** y conecta tu repositorio.
4. Configura:
   - **Runtime**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app` (ya viene definido en el `Procfile`, Render lo detecta solo)
5. Click en **Create Web Service**. Render instalará las dependencias y desplegará la app. En unos minutos tendrás una URL como `https://tu-app.onrender.com`.

### Sobre la persistencia de datos en Render

- **Plan gratuito**: el disco es efimero. Mientras la instancia siga activa, los cambios que hagas desde el panel de administrador (agregar/editar/vender vehiculos) se guardan con normalidad. Pero si el servicio se reinicia (por inactividad, redeploy, etc.) la base de datos vuelve a su estado inicial con los 30+ vehiculos de ejemplo.
- **Persistencia real (plan pago con disco)**:
  1. En el dashboard de Render, ve a tu servicio → **Disks** → **Add Disk**.
  2. Asigna un **Mount Path**, por ejemplo `/var/data`.
  3. En **Environment** agrega la variable `DATABASE_PATH` con el valor `/var/data/database.db`.
  4. Vuelve a desplegar. A partir de ahi la base de datos vive en el disco persistente y sobrevive a reinicios y redeploys.

## Notas tecnicas

- Las imagenes de los vehiculos se generan mediante placeholders con el nombre de marca/modelo (via placehold.co) para que el proyecto funcione sin necesidad de archivos de imagen locales. Puedes reemplazarlas subiendo tus propias imagenes a `static/img/` y actualizando el campo `image` de cada vehiculo desde el panel de administrador.
- El calculo de financiamiento utiliza la formula de amortizacion de cuota fija con una tasa de interes anual simulada del 12%.
- Los impuestos del carrito se calculan con una tasa simulada del 18%.
- Favoritos, carrito y comparador se almacenan en la sesion del navegador (cookies de sesion de Flask), por lo que son independientes por usuario/navegador.
- Al completar una compra, el vehiculo se marca automaticamente como "Vendido".

## Licencia

Proyecto de demostracion educativa. Libre uso y modificacion.
