import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import qrcode
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Card Suite V7", page_icon="🎨", layout="wide")

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

st.title("🎨 Suite de Diseño de Tarjetas")

# --- MOTOR DE FUENTES ---
def obtener_fuente(tipo, size):
    # Definimos la ruta de la fuente que YA tienes subida (Montserrat)
    ruta_montserrat = os.path.join(os.path.dirname(__file__), "Montserrat-Bold.ttf")

    try:
        if tipo == "Moderna (Montserrat)":
            return ImageFont.truetype(ruta_montserrat, int(size))

        elif tipo == "Tech (Monospace)":
            # Intentamos usar una fuente de sistema tipo código
            try:
                return ImageFont.truetype("DejaVuSansMono-Bold.ttf", int(size))
            except:
                return ImageFont.truetype("Courier", int(size))

        elif tipo == "Clásica (Serif)":
            # Intentamos usar una fuente con serifa
            try:
                return ImageFont.truetype("DejaVuSerif-Bold.ttf", int(size))
            except:
                # Si falla, usamos la default pero ajustamos tamaño
                return ImageFont.load_default()

        # Fallback por seguridad
        return ImageFont.truetype(ruta_montserrat, int(size))
    except:
        # Si todo falla (ej: archivo borrado), usar default
        return ImageFont.load_default()

def recortar_circulo(imagen_bytes, size):
    img = Image.open(imagen_bytes).convert("RGBA")
    mask = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + (size, size), fill=255)
    output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)
    return output

# --- BARRA LATERAL (CONTROLES) ---
with st.sidebar:
    st.header("1. Estilo y Diseño")
    diseno_seleccionado = st.selectbox("Plantilla de Diseño", ["Split Premium", "Full Brand (Oscuro)", "Minimalista (Claro)"])
    fuente_seleccionada = st.selectbox("Tipografía", ["Moderna (Montserrat)", "Tech (Monospace)", "Clásica (Serif)"])

    st.header("2. Tamaños (Zoom)")
    sz_nombre = st.slider("Tamaño Nombre", 40, 120, 75)
    sz_cargo = st.slider("Tamaño Cargo", 20, 80, 40)
    sz_texto = st.slider("Tamaño Contacto", 20, 60, 30)

    st.header("3. Colores")
    color_principal = st.color_picker("Color Principal", "#0A2540")
    color_texto_brand = st.color_picker("Color Texto (En fondos oscuros)", "#FFFFFF")

    st.header("4. Datos")
    nombre = st.text_input("Nombre", "Luis Jiménez")
    titulo = st.text_input("Cargo", "Full Stack Developer")
    telefono = st.text_input("WhatsApp", "+56 9 1234 5678")
    email = st.text_input("Email", "contacto@luisjimenez.dev")
    web = st.text_input("Web", "www.luisjimenez.dev")
    ubicacion = st.text_input("Ubicación", "Santiago, Chile")
    foto = st.file_uploader("Foto de Perfil", type=['png', 'jpg'])

# --- MOTORES DE RENDERIZADO (3 DISEÑOS) ---

def draw_split_premium(W, H, draw, img):
    # EL DISEÑO QUE YA CONOCES (IZQUIERDA COLOR / DERECHA BLANCO)
    ANCHO_PANEL = 400
    draw.rectangle([0, 0, ANCHO_PANEL, H], fill=color_principal)

    # Foto
    center_panel = int(ANCHO_PANEL / 2)
    if foto:
        avatar = recortar_circulo(foto, 240)
        img.paste(avatar, (center_panel - 120, 80), avatar)

    # QR
    try:
        qr = qrcode.make(f"https://wa.me/{telefono.replace('+','')}")
        qr = qr.resize((160, 160))
        img.paste(qr, (center_panel - 80, H - 200))
    except: pass

    # Textos Derecha
    X = ANCHO_PANEL + 80
    Y = 120
    draw.text((X, Y), nombre.upper(), font=obtener_fuente(fuente_seleccionada, sz_nombre), fill="#000")

    Y += sz_nombre + 20
    draw.rectangle([X, Y, X+50, Y+5], fill=color_principal)
    draw.text((X+70, Y-15), titulo, font=obtener_fuente(fuente_seleccionada, sz_cargo), fill="#555")

    Y += 100
    gap = sz_texto + 40
    datos = [("📞", telefono), ("✉️", email), ("🌐", web), ("📍", ubicacion)]
    for icon, txt in datos:
        if txt:
            draw.text((X, Y), icon, font=obtener_fuente("default", sz_texto), fill="#333")
            draw.text((X+60, Y), txt, font=obtener_fuente(fuente_seleccionada, sz_texto), fill="#333")
            Y += gap

def draw_full_brand(W, H, draw, img):
    # DISEÑO TODO COLOR (FONDO OSCURO, TEXTO CENTRADO)
    draw.rectangle([0, 0, W, H], fill=color_principal)

    # Foto Centrada Arriba
    if foto:
        avatar = recortar_circulo(foto, 200)
        img.paste(avatar, (int(W/2)-100, 50), avatar)

    # Nombre Centrado
    Y = 280
    f_nom = obtener_fuente(fuente_seleccionada, sz_nombre)
    w_n = draw.textbbox((0,0), nombre.upper(), font=f_nom)[2]
    draw.text(((W-w_n)/2, Y), nombre.upper(), font=f_nom, fill=color_texto_brand)

    # Cargo Centrado
    Y += sz_nombre + 10
    f_car = obtener_fuente(fuente_seleccionada, sz_cargo)
    w_c = draw.textbbox((0,0), titulo, font=f_car)[2]
    draw.text(((W-w_c)/2, Y), titulo, font=f_car, fill=color_texto_brand) # Acento cian

    # Datos Abajo (Columnas)
    Y += 100
    f_txt = obtener_fuente(fuente_seleccionada, sz_texto)

    # QR Esquina Derecha
    try:
        qr = qrcode.make(f"https://wa.me/{telefono}").resize((140,140))
        img.paste(qr, (W-180, H-180))
    except: pass

    # Lista izquierda
    X_list = 150
    gap = sz_texto + 30
    datos = [("📞", telefono), ("✉️", email), ("🌐", web)]
    for icon, txt in datos:
        if txt:
            draw.text((X_list, Y), f"{icon}  {txt}", font=f_txt, fill=color_texto_brand)
            Y += gap

def draw_minimalist(W, H, draw, img):
    # DISEÑO BLANCO LIMPIO
    draw.rectangle([0,0,W,H], fill="#FFFFFF")

    # Barra lateral fina de color
    draw.rectangle([0,0, 40, H], fill=color_principal)

    X = 100
    Y = 80

    # Nombre y Cargo alineado izquierda
    draw.text((X, Y), nombre.upper(), font=obtener_fuente(fuente_seleccionada, sz_nombre), fill="#000")
    Y += sz_nombre + 15
    draw.text((X, Y), titulo, font=obtener_fuente(fuente_seleccionada, sz_cargo), fill=color_principal)

    # Foto a la derecha flotando
    if foto:
        avatar = recortar_circulo(foto, 220)
        img.paste(avatar, (W-280, 60), avatar)

    # Datos abajo en grid
    Y = 350
    f_txt = obtener_fuente(fuente_seleccionada, sz_texto)
    gap = sz_texto + 40

    draw.text((X, Y), f"📞 {telefono}", font=f_txt, fill="#333")
    draw.text((X, Y+gap), f"✉️ {email}", font=f_txt, fill="#333")

    # Columna 2 de datos
    draw.text((X+400, Y), f"🌐 {web}", font=f_txt, fill="#333")
    draw.text((X+400, Y+gap), f"📍 {ubicacion}", font=f_txt, fill="#333")

    # QR pequeño al centro abajo
    try:
        qr = qrcode.make(f"https://wa.me/{telefono}").resize((120,120))
        img.paste(qr, (int(W/2)-60, H-150))
    except: pass


# --- CONTROLADOR PRINCIPAL ---
def generar_tarjeta():
    W, H = 1050, 600
    img = Image.new('RGB', (W, H), color="#FFFFFF")
    draw = ImageDraw.Draw(img)

    if diseno_seleccionado == "Split Premium":
        draw_split_premium(W, H, draw, img)
    elif diseno_seleccionado == "Full Brand (Oscuro)":
        draw_full_brand(W, H, draw, img)
    elif diseno_seleccionado == "Minimalista (Claro)":
        draw_minimalist(W, H, draw, img)

    return img

# --- VISTA PREVIA ---
st.subheader(f"Vista Previa: {diseno_seleccionado}")
tarjeta_final = generar_tarjeta()
st.image(tarjeta_final, use_container_width=True)

# Descarga
buf = io.BytesIO()
tarjeta_final.save(buf, format="PNG", resolution=300)
st.download_button("💾 Descargar Tarjeta HD", buf.getvalue(), "tarjeta_v7.png", "image/png")