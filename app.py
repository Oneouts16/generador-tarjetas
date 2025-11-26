import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import qrcode
import random

# Configuración de página
st.set_page_config(page_title="Card Studio Desktop", page_icon="💳", layout="wide")

# Estilos CSS para que parezca más App nativa
st.markdown("""
<style>
    .stApp { background-color: #111; }
    header {visibility: hidden;} /* Oculta el menú de hamburguesa de Streamlit */
    footer {visibility: hidden;} /* Oculta el pie de página */
</style>
""", unsafe_allow_html=True)

st.title("💳 Card Studio: Desktop Edition")

# --- TABS ---
tab_datos, tab_diseno, tab_ajustes = st.tabs(["📝 Datos", "🎨 Diseño & Logo", "⚙️ Calibración"])

# 1. PESTAÑA DATOS
with tab_datos:
    col_d1, col_d2 = st.columns(2)
    with col_d1:
        nombre = st.text_input("Nombre Completo", "Luis Jiménez")
        titulo = st.text_input("Cargo / Rol", "Desarrollador Web Full Stack")
        web = st.text_input("Sitio Web", "www.luisjimenez.dev")
    with col_d2:
        telefono = st.text_input("Móvil (WhatsApp)", "+56 9 1234 5678")
        email = st.text_input("Email", "contacto@luisjimenez.dev")
        servicios_input = st.text_area("Servicios (separados por coma)", "Desarrollo Web, Arquitectura Cloud, Ciberseguridad")

# 2. PESTAÑA DISEÑO
with tab_diseno:
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.subheader("Estilo Visual")
        color_fondo = st.color_picker("Fondo Principal", "#0A2540")
        color_acento = st.color_picker("Color Acento", "#00D4FF")
        color_texto_A = st.color_picker("Color Texto Nombre", "#FFFFFF")
        # NUEVO: Selector de Logo
        st.markdown("---")
        uploaded_logo = st.file_uploader("Subir Logo (Opcional - PNG transparente)", type=['png', 'jpg'])

    with col_c2:
        st.subheader("Textura Generativa")
        tipo_trama = st.selectbox("Estilo de Fondo", ["Grid Tecnológico", "Ninguna", "Lluvia Matrix", "Puntos"])
        intensidad_trama = st.slider("Opacidad de Trama", 10, 100, 40)

# 3. PESTAÑA CALIBRACIÓN (Valores por defecto AUMENTADOS)
with tab_ajustes:
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        st.markdown("**Cara A (Frente)**")
        # He aumentado los valores predeterminados (el último número)
        size_nombre = st.slider("Tamaño Nombre", 40, 150, 90)
        size_cargo = st.slider("Tamaño Cargo", 20, 80, 45)
        pos_y_logo = st.slider("Posición Vertical Elementos", 50, 300, 180)
    with col_a2:
        st.markdown("**Cara B (Reverso)**")
        size_textos_back = st.slider("Tamaño Textos Info", 20, 60, 35)

# --- MOTOR GRÁFICO ---
def cargar_fuente(size, bold=False):
    archivo = "Montserrat-Bold.ttf" if bold else "arial.ttf"
    try:
        return ImageFont.truetype(archivo, int(size))
    except:
        return ImageFont.load_default()

def dibujar_trama(draw, W, H, tipo, color, alpha):
    # Lógica de trama simplificada para rendimiento
    pass # Se maneja dentro de crear_tarjeta con overlay

def crear_tarjeta(lado):
    W, H = 1050, 600

    if lado == "Frente":
        img = Image.new('RGB', (W, H), color=color_fondo)

        # TRAMAS
        if tipo_trama != "Ninguna":
            overlay = Image.new('RGBA', (W, H), (0,0,0,0))
            draw_ov = ImageDraw.Draw(overlay)
            c_hex = color_acento.lstrip('#')
            c_rgb = tuple(int(c_hex[i:i+2], 16) for i in (0, 2, 4))
            color_trama = c_rgb + (intensidad_trama,)

            if tipo_trama == "Grid Tecnológico":
                step = 50
                for x in range(0, W, step): draw_ov.line((x,0, x,H), fill=color_trama, width=1)
                for y in range(0, H, step): draw_ov.line((0,y, W,y), fill=color_trama, width=1)
            elif tipo_trama == "Lluvia Matrix":
                font_m = cargar_fuente(25)
                for _ in range(80):
                    draw_ov.text((random.randint(0,W), random.randint(0,H)), random.choice(["0","1"]), font=font_m, fill=color_trama)

            img = Image.alpha_composite(img.convert('RGBA'), overlay).convert('RGB')

        draw = ImageDraw.Draw(img)

        # 1. LOGO (Imagen o Texto)
        y_cursor = pos_y_logo

        if uploaded_logo is not None:
            # Lógica para logo subido
            logo_img = Image.open(uploaded_logo).convert("RGBA")
            # Redimensionar manteniendo proporción (max alto 200px)
            aspect = logo_img.width / logo_img.height
            new_h = 200
            new_w = int(new_h * aspect)
            logo_img = logo_img.resize((new_w, new_h))

            # Pegar centrado
            x_pos = int((W - new_w) / 2)
            img.paste(logo_img, (x_pos, y_cursor - 50), logo_img) # Usamos la misma imagen como máscara
            y_cursor += 180 # Mover cursor hacia abajo
        else:
            # Lógica texto por defecto
            font_logo = cargar_fuente(140, bold=True)
            iniciales = "".join([n[0] for n in nombre.split()[:2]])
            txt_logo = f"< {iniciales} />"
            bbox = draw.textbbox((0, 0), txt_logo, font=font_logo)
            w_txt = bbox[2] - bbox[0]
            draw.text(((W-w_txt)/2, y_cursor), txt_logo, font=font_logo, fill=color_acento)
            y_cursor += 150

        # 2. NOMBRE
        font_nom = cargar_fuente(size_nombre, bold=True)
        bbox_n = draw.textbbox((0, 0), nombre.upper(), font=font_nom)
        draw.text(((W-(bbox_n[2]-bbox_n[0]))/2, y_cursor), nombre.upper(), font=font_nom, fill=color_texto_A)

        # 3. CARGO
        font_car = cargar_fuente(size_cargo, bold=False)
        bbox_c = draw.textbbox((0, 0), titulo, font=font_car)
        draw.text(((W-(bbox_c[2]-bbox_c[0]))/2, y_cursor + size_nombre + 15), titulo, font=font_car, fill="#A0AEC0")

        return img

    elif lado == "Reverso":
        img = Image.new('RGB', (W, H), color="#FFFFFF")
        draw = ImageDraw.Draw(img)

        # Fuentes dinámicas
        f_header = cargar_fuente(size_textos_back + 10, bold=True)
        f_text = cargar_fuente(size_textos_back, bold=False)
        f_bold = cargar_fuente(size_textos_back, bold=True)

        # Barra lateral
        draw.rectangle([0, 0, 40, H], fill=color_fondo)

        # Título
        draw.text((80, 50), "SERVICIOS", font=f_header, fill=color_fondo)
        draw.line((80, 100, 600, 100), fill=color_acento, width=4)

        # Servicios
        servicios_lista = [s.strip() for s in servicios_input.split(",")]
        y = 140
        for serv in servicios_lista:
            draw.rectangle([80, y+15, 90, y+25], fill=color_acento)
            draw.text((105, y), serv, font=f_text, fill="#333333")
            y += int(size_textos_back * 1.8)

        # Contacto
        y_contact = H - 220
        line_height = int(size_textos_back * 1.6)
        labels = [("TEL", telefono), ("MAIL", email), ("WEB", web)]

        for label, value in labels:
            draw.text((80, y_contact), f">> {label}:", font=f_bold, fill=color_fondo)
            draw.text((250, y_contact), value, font=f_text, fill="#333333")
            y_contact += line_height

        # QR
        try:
            qr = qrcode.QRCode(box_size=10, border=1)
            qr.add_data(f"https://wa.me/{telefono.replace('+','').replace(' ','')}")
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white").resize((200, 200))
            img.paste(qr_img, (W - 240, H - 240))
            draw.text((W - 225, H - 35), "Escanear Contacto", font=cargar_fuente(20, bold=True), fill=color_fondo)
        except: pass

        return img

# --- INTERFAZ ---
col1, col2 = st.columns(2)

def convert_image(img):
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

with col1:
    frente = crear_tarjeta("Frente")
    st.image(frente, use_container_width=True)
    st.download_button("💾 Descargar Frente", convert_image(frente), "frente.png", "image/png")

with col2:
    reverso = crear_tarjeta("Reverso")
    st.image(reverso, use_container_width=True)
    st.download_button("💾 Descargar Reverso", convert_image(reverso), "reverso.png", "image/png")