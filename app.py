import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io
import qrcode
import os

# --- CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="ProCard Studio", page_icon="💳", layout="wide")

# CSS AVANZADO: Ocultar marcas de Streamlit y estilizar botones
st.markdown("""
<style>
    .stApp { background-color: #0E1117; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        font-weight: bold;
        background-color: #00D4FF;
        color: #000;
        border: none;
    }
    .stButton>button:hover {
        background-color: #00A3CC;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

st.title("💳 ProCard Studio")
st.markdown("Diseño profesional de tarjetas con **Avatar Circular** y **Salida PDF**.")

# --- GESTOR DE FUENTES (ROBUSTO PARA NUBE) ---
def obtener_fuente(size, bold=False):
    # Intentamos cargar Montserrat Bold si existe
    ruta_directorio = os.path.dirname(os.path.abspath(__file__))
    nombre_archivo = "Montserrat-Bold.ttf" # Usamos la Bold para casi todo por estilo
    ruta_fuente = os.path.join(ruta_directorio, nombre_archivo)

    try:
        return ImageFont.truetype(ruta_fuente, int(size))
    except:
        # Fallback seguro
        return ImageFont.load_default()

# --- PROCESADOR DE IMAGEN CIRCULAR ---
def recortar_circulo(imagen_bytes, size):
    img = Image.open(imagen_bytes).convert("RGBA")
    # Crear máscara circular
    mask = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0) + (size, size), fill=255)

    # Ajustar imagen al tamaño y aplicar máscara
    output = ImageOps.fit(img, mask.size, centering=(0.5, 0.5))
    output.putalpha(mask)
    return output

# --- INTERFAZ ---
tab_contenido, tab_estilo, tab_exportar = st.tabs(["👤 Contenido & Foto", "🎨 Estilo Visual", "🖨️ Exportación"])

with tab_contenido:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Datos Personales")
        nombre = st.text_input("Nombre Completo", "Luis Jiménez")
        titulo = st.text_input("Cargo / Especialidad", "Full Stack Developer")
        web = st.text_input("Sitio Web", "www.luisjimenez.dev")
    with col2:
        st.subheader("Contacto")
        telefono = st.text_input("WhatsApp (Internacional)", "+56 9 1234 5678")
        email = st.text_input("Email Profesional", "contacto@luisjimenez.dev")
        # SUBIDA DE FOTO
        st.markdown("---")
        foto_upload = st.file_uploader("Subir Foto de Perfil (Se recortará en círculo)", type=['png', 'jpg', 'jpeg'])

with tab_estilo:
    c1, c2 = st.columns(2)
    with c1:
        color_fondo = st.color_picker("Fondo Tarjeta", "#0A2540")
        color_acento = st.color_picker("Color Detalles", "#00D4FF")
        color_texto = st.color_picker("Color Texto Principal", "#FFFFFF")
    with c2:
        st.info("Ajustes Avanzados")
        size_nombre = st.slider("Tamaño Nombre", 50, 120, 80)
        pos_y_elementos = st.slider("Posición Vertical Elementos", 50, 400, 150)

# --- MOTOR DE RENDERIZADO ---
def crear_tarjeta(lado):
    W, H = 1050, 600
    img = Image.new('RGB', (W, H), color=color_fondo if lado == "Frente" else "#FFFFFF")
    draw = ImageDraw.Draw(img)

    if lado == "Frente":
        # 1. Dibujar Foto o Logo Texto
        cursor_y = pos_y_elementos

        if foto_upload:
            # Procesar foto circular
            avatar_size = 220
            try:
                avatar = recortar_circulo(foto_upload, avatar_size)
                # Centrar
                x_pos = int((W - avatar_size) / 2)
                # Pegar usando la misma imagen como máscara alpha
                img.paste(avatar, (x_pos, cursor_y - 60), avatar)
                cursor_y += 180
            except:
                st.error("Error al procesar la imagen.")
        else:
            # Fallback a Logo de Texto
            f_logo = obtener_fuente(120)
            inic = "".join([n[0] for n in nombre.split()[:2]])
            txt = f"< {inic} />"
            bbox = draw.textbbox((0, 0), txt, font=f_logo)
            draw.text(((W-(bbox[2]-bbox[0]))/2, cursor_y), txt, font=f_logo, fill=color_acento)
            cursor_y += 140

        # 2. Textos
        f_nom = obtener_fuente(size_nombre)
        bbox_n = draw.textbbox((0, 0), nombre.upper(), font=f_nom)
        draw.text(((W-(bbox_n[2]-bbox_n[0]))/2, cursor_y), nombre.upper(), font=f_nom, fill=color_texto)

        f_cargo = obtener_fuente(40)
        bbox_c = draw.textbbox((0, 0), titulo, font=f_cargo)
        draw.text(((W-(bbox_c[2]-bbox_c[0]))/2, cursor_y + size_nombre + 10), titulo, font=f_cargo, fill="#A0AEC0")

    elif lado == "Reverso":
        # Decoración lateral
        draw.rectangle([0, 0, 30, H], fill=color_fondo)

        f_big = obtener_fuente(40)
        f_med = obtener_fuente(30)

        # Título
        draw.text((70, 50), "CONTACTO DIRECTO", font=f_big, fill=color_fondo)
        draw.line((70, 100, 500, 100), fill=color_acento, width=5)

        # Datos
        y = 150
        gap = 70
        datos = [
            ("📞", telefono),
            ("✉️", email),
            ("🌐", web)
        ]

        for icon, info in datos:
            # Icono simulado con texto (o podrías cargar imagenes de iconos reales)
            draw.text((70, y), icon, font=f_med, fill="#000") # Emoji simple
            draw.text((130, y), info, font=f_med, fill="#333333")
            y += gap

        # QR
        try:
            qr = qrcode.QRCode(box_size=10, border=1)
            qr.add_data(f"https://wa.me/{telefono.replace('+','').replace(' ','')}")
            qr.make(fit=True)
            qr_img = qr.make_image(fill_color="black", back_color="white").resize((220, 220))
            img.paste(qr_img, (W-260, H-260))
            draw.text((W-230, H-35), "Escanear", font=f_med, fill=color_fondo)
        except: pass

    return img

# --- VISTA PREVIA Y DESCARGA ---
frente = crear_tarjeta("Frente")
reverso = crear_tarjeta("Reverso")

col_v1, col_v2 = st.columns(2)

def guardar_img(img, formato="PNG"):
    buf = io.BytesIO()
    img.save(buf, format=formato, resolution=300) # 300 DPI para impresión
    return buf.getvalue()

with col_v1:
    st.image(frente, caption="Frente", use_container_width=True)
    # Botones descarga Frente
    b1, b2 = st.columns(2)
    with b1: st.download_button("🖼️ PNG Digital", guardar_img(frente, "PNG"), "frente.png", "image/png")
    with b2: st.download_button("📄 PDF Imprenta", guardar_img(frente, "PDF"), "frente.pdf", "application/pdf")

with col_v2:
    st.image(reverso, caption="Reverso", use_container_width=True)
    # Botones descarga Reverso
    b3, b4 = st.columns(2)
    with b3: st.download_button("🖼️ PNG Digital", guardar_img(reverso, "PNG"), "reverso.png", "image/png")
    with b4: st.download_button("📄 PDF Imprenta", guardar_img(reverso, "PDF"), "reverso.pdf", "application/pdf")