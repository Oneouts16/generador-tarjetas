import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import qrcode

# Configuración de la página
st.set_page_config(page_title="Card Gen Pro Fixed", page_icon="💳", layout="wide")

# Estilos CSS para una apariencia más limpia
st.markdown("""
<style>
    .stApp { background-color: #0e1117; color: white; }
    h1 { color: #00D4FF; }
    /* Ajustar el ancho de las imágenes de vista previa */
    [data-testid="stImage"] {
        max-width: 100%;
        margin: auto;
        border-radius: 15px;
        box-shadow: 0 10px 20px rgba(0,0,0,0.3);
    }
</style>
""", unsafe_allow_html=True)

st.title("💳 Generador de Tarjetas: Master Edition (Calibrado)")
st.markdown("Diseño de alta precisión con **centrado automático** y **textos legibles**.")

# --- BARRA LATERAL ---
with st.sidebar.expander("1. Datos Personales", expanded=True):
    nombre = st.text_input("Nombre", "Luis Jiménez")
    titulo = st.text_input("Cargo", "Desarrollador Web Full Stack")
    telefono = st.text_input("Celular", "+56 9 1234 5678")
    email = st.text_input("Email", "contacto@luisjimenez.dev")
    web = st.text_input("Web", "www.luisjimenez.dev")

with st.sidebar.expander("2. Colores y Estilo", expanded=True):
    color_fondo = st.color_picker("Fondo Cara A", "#0A2540")
    color_acento = st.color_picker("Color Acento (Logo/Detalles)", "#00D4FF")
    color_texto_A = st.color_picker("Color Texto Nombre", "#FFFFFF")

st.sidebar.markdown("---")
st.sidebar.header("🛠️ Calibración Fina")
# Sliders con valores por defecto ajustados para que se vea bien de entrada
size_logo = st.sidebar.slider("Tamaño Logo < >", 80, 250, 150)
size_nombre = st.sidebar.slider("Tamaño Nombre", 40, 120, 80)
# Este slider ahora controla la posición inicial superior
pos_y_inicio = st.sidebar.slider("Posición Vertical Inicio", 50, 250, 120)

# --- FUNCIONES AUXILIARES ---
def cargar_fuente(size, bold=False):
    # Intenta cargar Montserrat, si no, usa Arial como respaldo seguro
    archivo = "Montserrat-Bold.ttf" if bold else "arial.ttf"
    try:
        return ImageFont.truetype(archivo, int(size))
    except:
        # Fallback a una fuente de sistema si no encuentra el archivo
        try:
             return ImageFont.truetype("arial.ttf", int(size))
        except:
             return ImageFont.load_default()

def generar_qr(dato):
    qr = qrcode.QRCode(box_size=10, border=2)
    # Limpiamos el número para el enlace
    numero_limpio = dato.replace("+", "").replace(" ", "")
    qr.add_data(f"https://wa.me/{numero_limpio}")
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white").resize((200, 200))

# Función maestra para centrar texto horizontalmente
def dibujar_texto_centrado(draw, text, font, color, y_pos, canvas_width):
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x_pos = (canvas_width - text_width) / 2
    draw.text((x_pos, y_pos), text, font=font, fill=color)
    # Retorna la altura real del texto para calcular la siguiente posición
    return bbox[3] - bbox[1]

# --- MOTOR DE DIBUJO (CORREGIDO) ---
def crear_tarjeta(lado):
    W, H = 1050, 600 # Lienzo de alta resolución

    if lado == "Frente":
        img = Image.new('RGB', (W, H), color=color_fondo)
        draw = ImageDraw.Draw(img)

        # Fuentes basadas en los sliders
        font_logo = cargar_fuente(size_logo, bold=True)
        font_nom = cargar_fuente(size_nombre, bold=True)
        font_car = cargar_fuente(size_nombre * 0.5, bold=False) # Cargo proporcional al nombre

        # 1. Dibujar Logo y calcular su altura
        iniciales = "".join([n[0] for n in nombre.split()[:2]])
        txt_logo = f"< {iniciales} />"
        # Usamos el slider para la posición Y inicial
        y_cursor = pos_y_inicio
        h_logo = dibujar_texto_centrado(draw, txt_logo, font_logo, color_acento, y_cursor, W)

        # 2. Dibujar Nombre debajo (sin superponer)
        # Añadimos un espacio (gap) proporcional
        y_cursor += h_logo + 40
        h_nombre = dibujar_texto_centrado(draw, nombre.upper(), font_nom, color_texto_A, y_cursor, W)

        # 3. Dibujar Cargo debajo
        y_cursor += h_nombre + 25
        dibujar_texto_centrado(draw, titulo, font_car, "#A0AEC0", y_cursor, W)

        return img

    elif lado == "Reverso":
        img = Image.new('RGB', (W, H), color="#FFFFFF")
        draw = ImageDraw.Draw(img)

        # Fuentes MÁS GRANDES para el reverso
        font_header = cargar_fuente(45, bold=True)
        font_bold = cargar_fuente(35, bold=True)
        font_reg = cargar_fuente(35, bold=False)

        # Margen izquierdo
        MARGIN_X = 100

        # Barra lateral decorativa
        draw.rectangle([0, 0, 50, H], fill=color_fondo)

        # Encabezado
        draw.text((MARGIN_X, 60), "SOLUCIONES DIGITALES", font=font_header, fill=color_fondo)
        draw.line((MARGIN_X, 110, W-MARGIN_X, 110), fill=color_acento, width=5)

        # Lista de Servicios (Con más espacio)
        servicios = ["Desarrollo Web Full Stack", "Diseño UI/UX Responsivo", "Estrategia SEO & Performance"]
        y = 160
        gap_servicios = 70 # Más espacio entre líneas
        for s in servicios:
            # Viñeta cuadrada
            draw.rectangle([MARGIN_X, y+15, MARGIN_X+15, y+30], fill=color_acento)
            draw.text((MARGIN_X + 40, y), s, font=font_reg, fill="#333333")
            y += gap_servicios

        # Datos de Contacto (Alineados y más grandes)
        y_contact = 400
        gap_contacto = 60

        # Usamos etiquetas de texto en lugar de emojis para consistencia
        draw.text((MARGIN_X, y_contact), ">> MOVIL:", font=font_bold, fill=color_fondo)
        draw.text((MARGIN_X + 200, y_contact), telefono, font=font_reg, fill="#333333")

        draw.text((MARGIN_X, y_contact + gap_contacto), ">> EMAIL:", font=font_bold, fill=color_fondo)
        draw.text((MARGIN_X + 200, y_contact + gap_contacto), email, font=font_reg, fill="#333333")

        draw.text((MARGIN_X, y_contact + gap_contacto*2), ">> WEB:", font=font_bold, fill=color_fondo)
        draw.text((MARGIN_X + 200, y_contact + gap_contacto*2), web, font=font_reg, fill="#333333")

        # QR Code (Esquina inferior derecha)
        try:
            qr_img = generar_qr(telefono)
            # Posición calculada desde la esquina inferior derecha
            img.paste(qr_img, (W - 250, H - 250))
            draw.text((W - 230, H - 40), "Escanear WhatsApp", font=cargar_fuente(25, bold=True), fill=color_fondo)
        except:
            pass

        return img

# --- INTERFAZ ---
col1, col2 = st.columns(2)

with col1:
    st.subheader("Cara A (Branding)")
    frente = crear_tarjeta("Frente")
    # use_container_width=True ajusta la imagen al ancho de la columna
    st.image(frente, use_container_width=True)

    buf = io.BytesIO()
    frente.save(buf, format="PNG", resolution=300)
    st.download_button("💾 Descargar Frente HD", data=buf.getvalue(), file_name="frente_calibrado.png", mime="image/png")

with col2:
    st.subheader("Cara B (Info)")
    reverso = crear_tarjeta("Reverso")
    st.image(reverso, use_container_width=True)

    buf2 = io.BytesIO()
    reverso.save(buf2, format="PNG", resolution=300)
    st.download_button("💾 Descargar Reverso HD", data=buf2.getvalue(), file_name="reverso_calibrado.png", mime="image/png")