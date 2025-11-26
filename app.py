import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import qrcode
import os

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS
# -----------------------------------------------------------------------------
st.set_page_config(page_title="Corporate Card Generator", page_icon="👔", layout="wide")

# CSS para modo oscuro/claro y botones táctiles
st.markdown("""
<style>
    /* Ajuste general */
    .stApp { transition: background-color 0.5s ease; }

    /* Botones grandes y profesionales */
    .stButton>button {
        width: 100%;
        height: 50px;
        border-radius: 8px;
        background-color: #007bff; /* Azul Corporativo */
        color: white;
        font-weight: 600;
        border: none;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        transform: translateY(-2px);
    }

    /* Ocultar elementos de Streamlit */
    #MainMenu, header, footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. FUNCIONES AUXILIARES (LOGICA DE DISEÑO)
# -----------------------------------------------------------------------------

def cargar_fuente(size, es_bold=False):
    """Carga la fuente Montserrat o usa fallback si no existe."""
    try:
        # Intenta cargar la fuente local
        ruta = os.path.join(os.path.dirname(__file__), "Montserrat-Bold.ttf")
        return ImageFont.truetype(ruta, int(size))
    except:
        # Fallback para Linux/Windows si no hay archivo
        try:
            return ImageFont.truetype("DejaVuSans-Bold.ttf", int(size))
        except:
            return ImageFont.load_default()

def procesar_imagen_circular(uploaded_file, size):
    """Convierte cualquier imagen cuadrada/recta en un círculo perfecto."""
    if uploaded_file is None: return None
    try:
        img = Image.open(uploaded_file).convert("RGBA")
        mask = Image.new('L', (size, size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + (size, size), fill=255)
        output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
        output.putalpha(mask)
        return output
    except:
        return None

def redimensionar_logo(uploaded_file, max_height):
    """Ajusta el logo manteniendo la proporción."""
    if uploaded_file is None: return None
    try:
        img = Image.open(uploaded_file).convert("RGBA")
        aspect_ratio = img.width / img.height
        new_w = int(max_height * aspect_ratio)
        return img.resize((new_w, max_height))
    except:
        return None

# -----------------------------------------------------------------------------
# 3. INTERFAZ DE USUARIO (UI)
# -----------------------------------------------------------------------------

st.title("👔 Generador de Tarjetas Corporativas")
st.markdown("Crea una tarjeta profesional de **una sola cara** con diseño minimalista.")

# Control de Tema (Dark/Light Mode para la tarjeta)
col_mode, col_info = st.columns([1, 3])
with col_mode:
    tema = st.radio("Tema de la Tarjeta", ["Claro (Minimalista)", "Oscuro (Elegante)"])

# Colores según tema
if tema == "Claro (Minimalista)":
    BG_COLOR = "#FFFFFF"
    TXT_PRIMARY = "#000000"
    TXT_SECONDARY = "#555555"
    ACCENT_COLOR = "#007BFF" # Azul
else:
    BG_COLOR = "#1A1A1A"
    TXT_PRIMARY = "#FFFFFF"
    TXT_SECONDARY = "#AAAAAA"
    ACCENT_COLOR = "#00D4FF" # Cian

# Formulario en Columnas y Expander para limpieza visual
with st.container():
    c1, c2, c3 = st.columns(3)

    with c1:
        st.subheader("1. Identidad")
        nombre = st.text_input("Nombre Completo", "Luis Jiménez")
        cargo = st.text_input("Cargo / Puesto", "Senior Developer")
        empresa = st.text_input("Empresa", "Tech Solutions Inc.")
        slogan = st.text_input("Slogan (Opcional)", "Innovando el futuro")

    with c2:
        st.subheader("2. Contacto")
        telefono = st.text_input("Teléfono", "+56 9 1234 5678")
        email = st.text_input("Email", "contacto@luisjimenez.dev")
        web = st.text_input("Sitio Web (Para QR)", "www.luisjimenez.dev")
        direccion = st.text_input("Dirección", "Av. Providencia 123, Santiago")

    with c3:
        st.subheader("3. Imágenes")
        foto_upload = st.file_uploader("Tu Foto (Perfil)", type=['png', 'jpg', 'jpeg'])
        logo_upload = st.file_uploader("Logo Empresa", type=['png', 'jpg'])

# Validación simple
if not nombre or not cargo or not web:
    st.warning("⚠️ Por favor completa al menos Nombre, Cargo y Sitio Web para generar la tarjeta.")
    st.stop()

# -----------------------------------------------------------------------------
# 4. MOTOR DE RENDERIZADO (DISEÑO ONE-SIDE)
# -----------------------------------------------------------------------------

def generar_tarjeta_final():
    # Lienzo de Alta Resolución (1050x600 px - Estándar Tarjeta de Visita)
    W, H = 1050, 600
    img = Image.new('RGB', (W, H), color=BG_COLOR)
    draw = ImageDraw.Draw(img)

    # --- A. CABECERA (MARCA) ---
    # Barra lateral de acento
    draw.rectangle([0, 0, 25, H], fill=ACCENT_COLOR)

    # Logo Empresa (Arriba Derecha)
    logo_img = redimensionar_logo(logo_upload, 80)
    if logo_img:
        # Pegar logo
        img.paste(logo_img, (W - logo_img.width - 50, 40), logo_img)
    else:
        # Texto Empresa si no hay logo
        f_emp = cargar_fuente(40)
        w_e = draw.textbbox((0,0), empresa.upper(), font=f_emp)[2]
        draw.text((W - w_e - 50, 40), empresa.upper(), font=f_emp, fill=TXT_PRIMARY)

    # Slogan (Debajo del logo/empresa)
    if slogan:
        f_slo = cargar_fuente(20)
        w_s = draw.textbbox((0,0), slogan, font=f_slo)[2]
        draw.text((W - w_s - 50, 90 if not logo_img else 130), slogan, font=f_slo, fill=TXT_SECONDARY)

    # --- B. IDENTIDAD PERSONAL (IZQUIERDA) ---
    X_CONTENT = 80 # Margen desde la barra azul
    Y_CURSOR = 80

    # Foto de Perfil
    if foto_upload:
        avatar = procesar_imagen_circular(foto_upload, 200)
        if avatar:
            img.paste(avatar, (X_CONTENT, Y_CURSOR), avatar)
            # Decoración borde foto
            draw.ellipse((X_CONTENT-2, Y_CURSOR-2, X_CONTENT+202, Y_CURSOR+202), outline=ACCENT_COLOR, width=3)
    else:
        # Placeholder circular con iniciales
        draw.ellipse((X_CONTENT, Y_CURSOR, X_CONTENT+200, Y_CURSOR+200), fill="#DDDDDD", outline=ACCENT_COLOR, width=3)
        f_big = cargar_fuente(80)
        ini = "".join([n[0] for n in nombre.split()[:2]])
        w_i = draw.textbbox((0,0), ini, font=f_big)[2]
        draw.text((X_CONTENT + 100 - w_i/2, Y_CURSOR + 50), ini, font=f_big, fill="#555")

    # Nombre y Cargo (Debajo de la foto)
    Y_TEXTO = Y_CURSOR + 220
    f_nom = cargar_fuente(50)
    draw.text((X_CONTENT, Y_TEXTO), nombre, font=f_nom, fill=TXT_PRIMARY)

    f_car = cargar_fuente(30)
    draw.text((X_CONTENT, Y_TEXTO + 55), cargo.upper(), font=f_car, fill=ACCENT_COLOR)

    # --- C. DATOS Y QR (DERECHA / ABAJO) ---
    # Línea divisoria sutil
    draw.line((350, 180, 950, 180), fill="#DDDDDD" if tema=="Claro (Minimalista)" else "#444", width=2)

    # Grid de datos
    X_DATA = 350
    Y_DATA = 220
    GAP = 55
    f_data = cargar_fuente(26)

    datos = [
        ("📞", telefono),
        ("✉️", email),
        ("📍", direccion),
        ("🌐", web)
    ]

    for icon, txt in datos:
        if txt:
            draw.text((X_DATA, Y_DATA), icon, font=cargar_fuente(24), fill=TXT_PRIMARY)
            draw.text((X_DATA + 50, Y_DATA), txt, font=f_data, fill=TXT_SECONDARY)
            Y_DATA += GAP

    # Generación de QR (Esquina Inferior Derecha)
    try:
        qr = qrcode.QRCode(box_size=10, border=1)
        qr.add_data(f"https://{web.replace('https://','').replace('http://','')}")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").resize((160, 160))

        # Pegar QR
        img.paste(qr_img, (W - 200, H - 200))

        # Etiqueta QR
        f_small = cargar_fuente(18)
        draw.text((W - 190, H - 30), "ESCANEAR WEB", font=f_small, fill=TXT_SECONDARY)
    except:
        pass

    return img

# -----------------------------------------------------------------------------
# 5. VISTA PREVIA Y EXPORTACIÓN
# -----------------------------------------------------------------------------

st.write("---")
st.subheader("👁️ Vista Previa en Tiempo Real")

# Generar la imagen
img_final = generar_tarjeta_final()

# Mostrar en pantalla (Responsive)
st.image(img_final, caption=f"Vista Previa - {tema}", use_container_width=True)

# Botones de descarga
col_d1, col_d2 = st.columns(2)

# Buffer PNG
buf_png = io.BytesIO()
img_final.save(buf_png, format="PNG", resolution=300)
png_bytes = buf_png.getvalue()

# Buffer PDF
buf_pdf = io.BytesIO()
img_final.save(buf_pdf, format="PDF", resolution=300)
pdf_bytes = buf_pdf.getvalue()

with col_d1:
    st.download_button("🖼️ Descargar PNG (Imagen)", png_bytes, "mi_tarjeta.png", "image/png")

with col_d2:
    st.download_button("📄 Descargar PDF (Impresión)", pdf_bytes, "mi_tarjeta.pdf", "application/pdf")