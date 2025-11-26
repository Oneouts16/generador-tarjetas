import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import qrcode
import os # Importante para encontrar el archivo en la nube

# Configuración de página
st.set_page_config(page_title="Card Studio Cloud", page_icon="💳", layout="wide")

# Estilos CSS
st.markdown("""
<style>
    .stApp { background-color: #111; }
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

st.title("💳 Card Studio: Cloud Edition")

# --- FUNCION MAESTRA DE FUENTES ---
def obtener_fuente(size):
    # 1. Buscamos la ruta exacta del archivo Montserrat-Bold.ttf
    ruta_directorio = os.path.dirname(os.path.abspath(__file__))
    ruta_fuente = os.path.join(ruta_directorio, "Montserrat-Bold.ttf")

    try:
        # Intentamos cargar Montserrat
        return ImageFont.truetype(ruta_fuente, int(size))
    except:
        # Si falla, intentamos cargar una fuente de sistema Linux (DejaVuSans)
        try:
            return ImageFont.truetype("DejaVuSans.ttf", int(size))
        except:
            # Si todo falla, usamos la defecto (fea pero legible)
            return ImageFont.load_default()

# --- INPUTS ---
tab_datos, tab_diseno, tab_ajustes = st.tabs(["📝 Datos", "🎨 Diseño", "⚙️ Ajustes"])

with tab_datos:
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre", "Luis Jiménez")
        titulo = st.text_input("Cargo", "Desarrollador Web Full Stack")
        web = st.text_input("Web", "www.luisjimenez.dev")
    with col2:
        telefono = st.text_input("WhatsApp", "+56 9 1234 5678")
        email = st.text_input("Email", "contacto@luisjimenez.dev")
        servicios_input = st.text_area("Servicios", "Desarrollo Web, Arquitectura Cloud, Ciberseguridad")

with tab_diseno:
    c1, c2 = st.columns(2)
    with c1:
        color_fondo = st.color_picker("Fondo", "#0A2540")
        color_acento = st.color_picker("Acento", "#00D4FF")
        color_texto = st.color_picker("Texto Nombre", "#FFFFFF")
    with c2:
        st.info("Tip: Si el texto se ve pequeño, usa la pestaña 'Ajustes'.")

with tab_ajustes:
    st.write("Calibración de Tamaños:")
    c_a1, c_a2 = st.columns(2)
    with c_a1:
        s_nombre = st.slider("Tamaño Nombre", 40, 150, 90)
        s_cargo = st.slider("Tamaño Cargo", 20, 80, 45)
    with c_a2:
        s_info = st.slider("Tamaño Info Reverso", 20, 60, 35)

# --- GENERADOR ---
def crear_tarjeta(lado):
    W, H = 1050, 600

    if lado == "Frente":
        img = Image.new('RGB', (W, H), color=color_fondo)
        draw = ImageDraw.Draw(img)

        # Logo
        font_logo = obtener_fuente(140)
        iniciales = "".join([n[0] for n in nombre.split()[:2]])
        txt_logo = f"< {iniciales} />"

        bbox = draw.textbbox((0, 0), txt_logo, font=font_logo)
        draw.text(((W-(bbox[2]-bbox[0]))/2, 180), txt_logo, font=font_logo, fill=color_acento)

        # Nombre
        font_nom = obtener_fuente(s_nombre)
        bbox_n = draw.textbbox((0, 0), nombre.upper(), font=font_nom)
        draw.text(((W-(bbox_n[2]-bbox_n[0]))/2, 330), nombre.upper(), font=font_nom, fill=color_texto)

        # Cargo
        font_car = obtener_fuente(s_cargo)
        bbox_c = draw.textbbox((0, 0), titulo, font=font_car)
        draw.text(((W-(bbox_c[2]-bbox_c[0]))/2, 330 + s_nombre), titulo, font=font_car, fill="#A0AEC0")

        return img

    elif lado == "Reverso":
        img = Image.new('RGB', (W, H), color="#FFFFFF")
        draw = ImageDraw.Draw(img)

        f_main = obtener_fuente(s_info)
        f_big = obtener_fuente(s_info + 10)

        # Decoracion
        draw.rectangle([0, 0, 40, H], fill=color_fondo)
        draw.text((80, 50), "SERVICIOS", font=f_big, fill=color_fondo)
        draw.line((80, 100, 600, 100), fill=color_acento, width=4)

        # Lista
        y = 140
        for s in servicios_input.split(","):
            draw.rectangle([80, y+15, 90, y+25], fill=color_acento)
            draw.text((105, y), s.strip(), font=f_main, fill="#333333")
            y += int(s_info * 1.8)

        # Contacto
        y_c = H - 220
        for label, val in [("TEL", telefono), ("MAIL", email), ("WEB", web)]:
            draw.text((80, y_c), f">> {label}:", font=f_main, fill=color_fondo)
            draw.text((250, y_c), val, font=f_main, fill="#333333")
            y_c += int(s_info * 1.6)

        # QR
        try:
            qr = qrcode.QRCode(box_size=10, border=1)
            qr.add_data(f"https://wa.me/{telefono.replace('+','')}")
            qr.make(fit=True)
            img.paste(qr.make_image(fill_color="black", back_color="white").resize((200, 200)), (W-240, H-240))
        except: pass

        return img

# --- VISUALIZACIÓN ---
c1, c2 = st.columns(2)
def a_bytes(img):
    b = io.BytesIO()
    img.save(b, format="PNG")
    return b.getvalue()

with c1:
    f = crear_tarjeta("Frente")
    st.image(f, use_container_width=True)
    st.download_button("Descargar Frente", a_bytes(f), "frente.png", "image/png")

with c2:
    r = crear_tarjeta("Reverso")
    st.image(r, use_container_width=True)
    st.download_button("Descargar Reverso", a_bytes(r), "reverso.png", "image/png")