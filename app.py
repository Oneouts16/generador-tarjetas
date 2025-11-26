import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import qrcode
import os

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="OneSide Card", page_icon="💳", layout="wide")

st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    #MainMenu, header, footer {visibility: hidden;}
    .stButton>button {
        width: 100%;
        border-radius: 12px;
        background-color: #00D4FF;
        color: #000;
        font-weight: bold;
        border: none;
        padding: 10px;
    }
    .stButton>button:hover { background-color: #00A3CC; color: white; }
</style>
""", unsafe_allow_html=True)

st.title("💳 OneSide Card Studio")
st.markdown("Diseño profesional **Todo en Uno**: Foto, Datos y QR en una sola cara.")

# --- FUNCIONES GRÁFICAS ---
def obtener_fuente(size, bold=False):
    ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Montserrat-Bold.ttf")
    try:
        return ImageFont.truetype(ruta, int(size))
    except:
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
col_inputs, col_preview = st.columns([1, 1.5])

with col_inputs:
    with st.expander("1. Datos Personales", expanded=True):
        nombre = st.text_input("Nombre", "Luis Jiménez")
        titulo = st.text_input("Cargo", "Full Stack Developer")

    with st.expander("2. Contacto"):
        telefono = st.text_input("WhatsApp", "+56 9 1234 5678")
        email = st.text_input("Email", "contacto@luisjimenez.dev")
        web = st.text_input("Web", "www.luisjimenez.dev")
        ubicacion = st.text_input("Ubicación (Opcional)", "Santiago, Chile")

    with st.expander("3. Imagen y Estilo"):
        foto = st.file_uploader("Tu Foto (Se hará circular)", type=['png', 'jpg'])
        st.write("---")
        color_panel = st.color_picker("Color Panel Izquierdo", "#0A2540")
        color_texto_panel = st.color_picker("Color Texto Panel", "#FFFFFF")
        color_texto_info = st.color_picker("Color Texto Info", "#333333")

# --- MOTOR DE RENDERIZADO (DISEÑO SPLIT) ---
def crear_tarjeta_unica():
    W, H = 1050, 600
    # Fondo blanco general
    img = Image.new('RGB', (W, H), color="#FFFFFF")
    draw = ImageDraw.Draw(img)

    # --- PANEL IZQUIERDO (35% del ancho) ---
    ANCHO_PANEL = 380
    draw.rectangle([0, 0, ANCHO_PANEL, H], fill=color_panel)

    # 1. FOTO DE PERFIL (Arriba en el panel)
    center_x_panel = int(ANCHO_PANEL / 2)

    if foto:
        try:
            size_foto = 220
            avatar = recortar_circulo(foto, size_foto)
            img.paste(avatar, (center_x_panel - int(size_foto/2), 60), avatar)
        except:
            st.error("Error en la imagen")
    else:
        # Si no hay foto, ponemos iniciales
        f_ini = obtener_fuente(100)
        ini = "".join([n[0] for n in nombre.split()[:2]])
        bbox = draw.textbbox((0,0), ini, font=f_ini)
        w_ini = bbox[2]-bbox[0]
        draw.text((center_x_panel - w_ini/2, 120), ini, font=f_ini, fill=color_texto_panel)

    # 2. CÓDIGO QR (Abajo en el panel)
    try:
        qr = qrcode.QRCode(box_size=10, border=2) # Border 2 para que tenga margen blanco
        qr.add_data(f"https://wa.me/{telefono.replace('+','').replace(' ','')}")
        qr.make(fit=True)
        # QR blanco con negro
        qr_img = qr.make_image(fill_color="black", back_color="white").resize((180, 180))

        # Posición QR
        y_qr = H - 220
        img.paste(qr_img, (center_x_panel - 90, y_qr))

        # Texto "Escanear"
        f_small = obtener_fuente(20)
        draw.text((center_x_panel - 40, y_qr + 190), "WhatsApp", font=f_small, fill=color_texto_panel)
    except:
        pass

    # --- PANEL DERECHO (Información) ---
    X_START = ANCHO_PANEL + 60
    Y_CURSOR = 100

    # 3. NOMBRE Y CARGO
    f_nombre = obtener_fuente(65) # Fuente grande
    draw.text((X_START, Y_CURSOR), nombre.upper(), font=f_nombre, fill="#000000")

    Y_CURSOR += 80
    f_cargo = obtener_fuente(35)
    # Dibujamos rectángulo decorativo pequeño bajo el nombre
    draw.rectangle([X_START, Y_CURSOR + 5, X_START + 50, Y_CURSOR + 10], fill=color_panel)
    draw.text((X_START + 70, Y_CURSOR - 5), titulo, font=f_cargo, fill="#666666")

    # 4. LISTA DE CONTACTOS
    Y_CURSOR += 120
    f_info = obtener_fuente(28)
    GAP = 65

    # Lista de datos con iconos de texto
    datos = [
        ("📞", telefono),
        ("✉️", email),
        ("🌐", web)
    ]
    if ubicacion:
        datos.append(("📍", ubicacion))

    for icon, text in datos:
        if text: # Solo si escribieron algo
            draw.text((X_START, Y_CURSOR), icon, font=f_info, fill="#000")
            draw.text((X_START + 50, Y_CURSOR), text, font=f_info, fill=color_texto_info)
            Y_CURSOR += GAP

    return img

# --- VISUALIZACIÓN ---
with col_preview:
    st.subheader("Vista Previa")
    tarjeta = crear_tarjeta_unica()
    st.image(tarjeta, use_container_width=True)

    # Función descarga
    def convert_img(img, fmt="PNG"):
        buf = io.BytesIO()
        img.save(buf, format=fmt, resolution=300)
        return buf.getvalue()

    c1, c2 = st.columns(2)
    with c1:
        st.download_button("💾 Descargar PNG", convert_img(tarjeta, "PNG"), "tarjeta.png", "image/png")
    with c2:
        st.download_button("📄 Descargar PDF", convert_img(tarjeta, "PDF"), "tarjeta.pdf", "application/pdf")