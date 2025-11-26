import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import qrcode
import os

# 1. CONFIGURACIÓN DE PÁGINA
# layout="centered" funciona mejor en móviles para enfocar la vista.
st.set_page_config(page_title="Card Pro Mobile", page_icon="📱", layout="centered")

# 2. ESTILOS CSS AVANZADOS (RESPONSIVE)
st.markdown("""
<style>
    /* Fondo general adaptable */
    .stApp { background-color: #0E1117; }

    /* Ocultar elementos innecesarios de Streamlit */
    #MainMenu, header, footer {visibility: hidden;}

    /* BOTONES TÁCTILES: Más grandes y anchos para dedos */
    .stButton>button {
        width: 100%;
        height: 50px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 16px;
        border: none;
        transition: 0.3s;
    }

    /* Contenedor de la vista previa */
    .preview-container {
        border: 2px solid #333;
        border-radius: 10px;
        padding: 10px;
        background-color: #1a1a1a;
    }
</style>
""", unsafe_allow_html=True)

st.title("📱 Generador de Tarjetas Pro")
st.markdown("Diseña, visualiza y descarga en segundos.")

# --- 3. MOTOR DE FUENTES ROBUSTO (Anti-Hormigas) ---
def obtener_fuente(size):
    # Intentamos cargar Montserrat (Tu fuente personalizada)
    try:
        ruta = os.path.join(os.path.dirname(__file__), "Montserrat-Bold.ttf")
        return ImageFont.truetype(ruta, int(size))
    except:
        # Fallback inteligente para Linux/Nube
        try:
            return ImageFont.truetype("DejaVuSans-Bold.ttf", int(size))
        except:
            return ImageFont.load_default()

# --- 4. FUNCIÓN DE RECORTE CIRCULAR ---
def recortar_circulo(imagen_bytes, size):
    img = Image.open(imagen_bytes).convert("RGBA")
    mask = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + (size, size), fill=255)
    output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)
    return output

# --- 5. INTERFAZ DE USUARIO (UI) ---

# A. CONTROL DE MODO (OSCURO / CLARO)
# Esto define los colores por defecto antes de que el usuario toque nada.
modo = st.radio("Tema Visual", ["Modo Oscuro", "Modo Claro"], horizontal=True)

if modo == "Modo Oscuro":
    def_panel = "#0A2540"  # Azul Navy
    def_bg = "#FFFFFF"     # Fondo blanco para la tarjeta (contraste)
    def_txt_panel = "#FFFFFF"
else:
    def_panel = "#F0F2F6"  # Gris claro muy elegante
    def_bg = "#FFFFFF"
    def_txt_panel = "#333333"

# B. FORMULARIO EN ACORDEÓN (Para ahorrar espacio en móviles)
with st.expander("📝 1. Editar Información", expanded=True):
    nombre = st.text_input("Nombre", "Luis Jiménez")
    titulo = st.text_input("Cargo", "Full Stack Developer")
    telefono = st.text_input("WhatsApp", "+56 9 1234 5678")
    email = st.text_input("Email", "contacto@luisjimenez.dev")
    web = st.text_input("Web", "www.luisjimenez.dev")
    ubicacion = st.text_input("Ubicación", "Santiago, Chile")

with st.expander("🎨 2. Personalizar Diseño"):
    foto = st.file_uploader("Subir Foto", type=['png', 'jpg'])
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        color_panel = st.color_picker("Color Panel Lateral", def_panel)
    with col_c2:
        # Slider de tamaño para ajuste fino
        zoom_nombre = st.slider("Tamaño Nombre", 50, 100, 75)

# --- 6. MOTOR DE RENDERIZADO (Split Layout) ---
def generar_tarjeta():
    W, H = 1050, 600
    img = Image.new('RGB', (W, H), color="#FFFFFF")
    draw = ImageDraw.Draw(img)

    # --- PANEL IZQUIERDO ---
    ANCHO_PANEL = 380
    draw.rectangle([0, 0, ANCHO_PANEL, H], fill=color_panel)

    center_panel = int(ANCHO_PANEL / 2)

    # FOTO
    if foto:
        try:
            size_foto = 220
            avatar = recortar_circulo(foto, size_foto)
            img.paste(avatar, (center_panel - 110, 70), avatar)
        except: pass
    else:
        # Iniciales
        f_ini = obtener_fuente(100)
        ini = "".join([n[0] for n in nombre.split()[:2]])
        bbox = draw.textbbox((0,0), ini, font=f_ini)
        draw.text((center_panel - (bbox[2]-bbox[0])/2, 120), ini, font=f_ini, fill="white")

    # QR
    try:
        qr = qrcode.QRCode(box_size=10, border=1)
        qr.add_data(f"https://wa.me/{telefono.replace('+','').replace(' ','')}")
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white").resize((160, 160))
        img.paste(qr_img, (center_panel - 80, H - 210))
    except: pass

    # --- PANEL DERECHO ---
    X = ANCHO_PANEL + 60
    Y = 110

    # Nombre (Color depende del modo o es negro por defecto en fondo blanco)
    draw.text((X, Y), nombre.upper(), font=obtener_fuente(zoom_nombre), fill="#111")

    # Cargo
    Y += zoom_nombre + 15
    draw.rectangle([X, Y, X+50, Y+6], fill=color_panel) # Detalle visual
    draw.text((X+60, Y-10), titulo, font=obtener_fuente(38), fill="#555")

    # Datos
    Y += 110
    f_info = obtener_fuente(28)
    gap = 65
    datos = [("📞", telefono), ("✉️", email), ("🌐", web), ("📍", ubicacion)]

    for icon, txt in datos:
        if txt:
            draw.text((X, Y), icon, font=obtener_fuente(26), fill="#333")
            draw.text((X+50, Y), txt, font=f_info, fill="#333")
            Y += gap

    return img

# --- 7. ZONA DE VISTA PREVIA Y DESCARGA ---
st.write("---")
st.subheader("👁️ Vista Previa")

# Generamos la tarjeta en memoria
tarjeta_final = generar_tarjeta()

# Mostramos la imagen (use_container_width=True hace que se adapte al ancho del celular)
st.image(tarjeta_final, caption="Diseño Final", use_container_width=True)

# Preparamos los archivos para descarga
buf_png = io.BytesIO()
tarjeta_final.save(buf_png, format="PNG", resolution=300)

buf_pdf = io.BytesIO()
tarjeta_final.save(buf_pdf, format="PDF", resolution=300)

# Botones de Acción (Columnas para que queden lado a lado en PC, apilados en móvil)
c1, c2 = st.columns(2)
with c1:
    st.download_button("🖼️ Descargar PNG", buf_png.getvalue(), "tarjeta.png", "image/png")
with c2:
    st.download_button("📄 Descargar PDF", buf_pdf.getvalue(), "tarjeta.pdf", "application/pdf")