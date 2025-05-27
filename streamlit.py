import streamlit as st
import pandas as pd
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder
import os

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(page_title="Asistente de Vivienda Altoandina", layout="centered")
st.title("🏠 Asistente de Vivienda Altoandina")
st.markdown("Responde el formulario y recibe el plano referencial más adecuado.")

# --- FORMULARIO DE ENTRADA ---
with st.form("formulario_consulta"):
    frontis = st.number_input("Frontis del terreno (m)", min_value=2.0, max_value=100.0, value=8.0, step=0.5)
    profundidad = st.number_input("Profundidad del terreno (m)", min_value=2.0, max_value=100.0, value=10.0, step=0.5)
    area = frontis * profundidad
    st.write(f"Área calculada: {area:.1f} m²")

    forma_terreno = st.selectbox(
        "Forma aproximada del terreno",
        ["Cuadrado", "Rectangular", "Alargado", "Irregular"]
    )

    tipologia = st.selectbox(
        "Tipología de planta deseada (opcional)",
        ["No especifica", "Compacta", "En L", "En U", "Lineal (I)"]
    )

    dormitorios = st.slider(
        "Número de dormitorios requeridos",
        min_value=2, max_value=5, value=2
    )

    productivo = st.checkbox(
        "Incluir espacio productivo (bodega + huerto + corrales)"
    )

    enviar = st.form_submit_button("Obtener esquema recomendado")

# --- PROCESAMIENTO ---
if enviar:
    # Cargar dataset
    df = pd.read_csv("dataset.csv", encoding="utf-8")
    # Calcular área en el dataset si no existe
    if "Frontis" in df.columns and "Profundidad" in df.columns:
        df["Área"] = df["Frontis"] * df["Profundidad"]

    # Configurar y entrenar modelo
    # Codificadores
    le_forma = LabelEncoder().fit(df["Forma aproximada del terreno"])
    le_tipologia = LabelEncoder().fit(df["Tipología de planta deseada"])
    le_productivo = LabelEncoder().fit(df["Espacio productivo"])

    # Preparar entrada
    entrada = pd.DataFrame({
        "Área": [area],
        "Forma aproximada del terreno": [forma_terreno],
        "Tipología de planta deseada": [tipologia],
        "Dormitorios": [dormitorios],
        "Espacio productivo": ["Sí" if productivo else "No"]
    })

    # Transformar
    entrada["Forma aproximada del terreno"] = le_forma.transform(entrada["Forma aproximada del terreno"])
    entrada["Tipología de planta deseada"] = le_tipologia.transform(entrada["Tipología de planta deseada"])
    entrada["Espacio productivo"] = le_productivo.transform(entrada["Espacio productivo"])

    df["Forma aproximada del terreno"] = le_forma.transform(df["Forma aproximada del terreno"])
    df["Tipología de planta deseada"] = le_tipologia.transform(df["Tipología de planta deseada"])
    df["Espacio productivo"] = le_productivo.transform(df["Espacio productivo"])

    # Variables de entrenamiento
    X = df[["Área", "Forma aproximada del terreno", "Tipología de planta deseada", "Dormitorios", "Espacio productivo"]]
    y = df["Nombre del plano"]

    modelo = KNeighborsClassifier(n_neighbors=1)
    modelo.fit(X, y)

    # Predicción
    resultado = modelo.predict(entrada)[0]

    st.success("Plano recomendado:")
    ruta_imagen = os.path.join("planos", resultado)
    if os.path.exists(ruta_imagen):
        st.image(ruta_imagen, caption=resultado)
    else:
        st.warning(f"No se encontró la imagen: {resultado}")
