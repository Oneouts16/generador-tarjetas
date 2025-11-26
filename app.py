import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import qrcode
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Card Pro", page_icon="💎", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    #MainMenu, header, footer {visibility: hidden;}
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background-color: #00D4FF;
        color: #000;
        font-weight: 800;
        border: none;
        padding: 12px;
        text-transform: uppercase;
    }
    .stButton>button:hover { background-color: #00A3CC; color: white; }
</style>
""", unsafe_allow_html=True)

st.title("💎 Generador de Tarjetas Premium")

# --- MOTOR DE FUENTES INTELIGENTE (ESTO ARREGLA EL TAMAÑO) ---
def obtener_fuente(size):
    # 1. Intentar cargar TU fuente (Montserrat)
    try:
        ruta_local = os.path.join(os.path.dirname(__file__), "Montserrat-Bold.ttf")
        return ImageFont.truetype(ruta_local, int(size))
    except:
        # 2. Si falla, intentar cargar fuente de Linux (Nube)
        try:
            return ImageFont.truetype("DejaVuSans-Bold.ttf", int(size))
        except:
            # 3. Si todo falla, intentar cargar arial (Windows)
            try:
                return ImageFont.truetype("arial.ttf", int(size))
            except:
                # 4. Último recurso (no debería llegar aquí)
                return ImageFont.load_default()

def recortar_circulo(imagen_bytes, size):
    img = Image.open(imagen_bytes).convert("RGBA")
    mask = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + (size, size), fill=255)
    output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)
    return output

# --- INTERFAZ ---
col_izq, col_der = st.columns([1, 1.5])

with col_izq:
    st.write("### 1. Información")
    nombre = st.text_input("Nombre", "Luis Jiménez")
    titulo = st.text_input("Cargo", "Full Stack Developer")

    st.write("### 2. Contacto")
    telefono = st.text_input("WhatsApp", "+56 9 1234 5678")
    email = st.text_input("Email", "contacto@luisjimenez.dev")
    web = st.text_input("Web", "www.luisjimenez.dev")
    ubicacion = st.text_input("Ubicación", "Santiago, Chile")

    st.write("### 3. Personalización")
    foto = st.file_uploader("Foto de Perfil", type=['png', 'jpg', 'jpeg'])
    color_panel = st.color_picker("Color Panel Izquierdo", "#0A2540")

# --- RENDERIZADO ---
def crear_tarjeta():
    # Lienzo Alta Resolución (1050x600)
    W, H = 1050, 600
    img = Image.new('RGB', (W, H), color="#FFFFFF")
    draw = ImageDraw.Draw(img)

    # --- PANEL IZQUIERDO (Color) ---
    ANCHO_PANEL = 400
    draw.rectangle([0, 0, ANCHO_PANEL, H], fill=color_panel)

    center_panel = int(ANCHO_PANEL / 2)

    # FOTO (Más grande)
    if foto:
        try:
            size_foto = 240
            avatar = recortar_circulo(foto, size_foto)
            # Centrar foto verticalmente en la mitad superior
            img.paste(avatar, (center_panel - int(size_foto/2), 80), avatar)
        except:
            pass
    else:
        # Iniciales si no hay foto
        f_ini = obtener_fuente(120)
        ini = "".join([n[0] for n in nombre.split()[:2]])
        bbox = draw.textbbox((0,0), ini, font=f_ini)
        draw.text((center_panel - (bbox[2]-bbox[0])/2, 140), ini, font=f_ini, fill="white")

    # QR (Más grande y abajo)
    try:
        qr = qrcode.QRCode(box_size=10, border=2)
        qr.add_data(f"https://wa.me/{telefono.replace('+','').replace(' ','')}")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").resize((160, 160))

        y_qr = H - 200
        img.paste(qr_img, (center_panel - 80, y_qr))
    except: pass

    # --- PANEL DERECHO (Texto Gigante) ---
    X_START = ANCHO_PANEL + 80 # Margen generoso
    Y_CURSOR = 120 # Bajamos un poco el inicio para centrar mejor

    # 1. NOMBRE (GIGANTE)
    f_nombre = obtener_fuente(75) # AUMENTADO de 65 a 75
    draw.text((X_START, Y_CURSOR), nombre.upper(), font=f_nombre, fill="#111111")

    # 2. CARGO
    Y_CURSOR += 90
    f_cargo = obtener_fuente(40) # AUMENTADO de 35 a 40
    # Línea decorativa
    draw.rectangle([X_START, Y_CURSOR + 15, X_START + 60, Y_CURSOR + 20], fill=color_panel)
    draw.text((X_START + 80, Y_CURSOR), titulo, font=f_cargo, fill="#555555")

    # 3. DATOS CONTACTO
    Y_CURSOR += 130
    f_info = obtener_fuente(32) # AUMENTADO de 28 a 32 (Mucho más legible)
    GAP = 70

    datos = [("📞", telefono), ("✉️", email), ("🌐", web), ("📍", ubicacion)]

    for icon, text in datos:
        if text:
            # Icono
            draw.text((X_START, Y_CURSOR), icon, font=obtener_fuente(28), fill="#333")
            # Texto
            draw.text((X_START + 60, Y_CURSOR), text, font=f_info, fill="#333333")
            Y_CURSOR += GAP

    return img

# --- MUESTRA ---
with col_der:
    st.write("### Vista Previa")
    tarjeta = crear_tarjeta()
    st.image(tarjeta, use_container_width=True)

    buf = io.BytesIO()
    tarjeta.save(buf, format="PNG", resolution=300)
    st.download_button("💾 Descargar Tarjeta HD", buf.getvalue(), "tarjeta_pro.png", "image/png")