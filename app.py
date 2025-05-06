import streamlit as st
import oci
import base64
from PIL import Image
from io import BytesIO
from oci.ai_vision import AIServiceVisionClient
from oci.ai_vision.models import InlineImageDetails, ImageFeature, AnalyzeImageDetails
from config import COMPARTMENT_ID

st.set_page_config(page_title="Análisis de Imágenes con OCI Vision")
st.title("Análisis de Imágenes con OCI Vision")

uploaded_file = st.file_uploader("Sube una imagen", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image_bytes = uploaded_file.read()
    image = Image.open(BytesIO(image_bytes))

    # Mostrar imagen reducida con opción de expandir
    with st.expander("Haz clic para ver la imagen en tamaño completo"):
        st.image(image, caption="Imagen subida (tamaño completo)", use_column_width=True)
    st.image(image.resize((int(image.width * 0.5), int(image.height * 0.5))), caption="Imagen subida (vista previa)")

    # Mostrar selección de servicio después de cargar imagen
    st.markdown("### Selecciona el servicio de análisis")
    selected_feature = st.selectbox("", [
        "Image Classification",
        "Object Detection",
        "Text Detection",
        "Face Detection"
    ])

    # Preparar cliente OCI
    config = oci.config.from_file("~/.oci/config")
    client = AIServiceVisionClient(config)

    # Codificar imagen en base64
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    image_details = InlineImageDetails(
        source="INLINE",
        data=image_base64
    )

    # Configurar feature y análisis
    if selected_feature == "Image Classification":
        features = [ImageFeature(feature_type="IMAGE_CLASSIFICATION")]
    elif selected_feature == "Object Detection":
        features = [ImageFeature(feature_type="OBJECT_DETECTION")]
    elif selected_feature == "Text Detection":
        features = [ImageFeature(feature_type="TEXT_DETECTION")]
    elif selected_feature == "Face Detection":
        features = [ImageFeature(feature_type="FACE_DETECTION")]
    else:
        features = []

    request = AnalyzeImageDetails(
        image=image_details,
        features=features,
        compartment_id=COMPARTMENT_ID
    )

    st.markdown("Procesando...")
    try:
        response = client.analyze_image(request)

        if selected_feature == "Text Detection":
            st.subheader("Texto detectado:")
            if response.data.image_text and response.data.image_text.lines:
                for line in response.data.image_text.lines:
                    st.write(line.text)
            else:
                st.info("No se detectó texto en la imagen.")

        elif selected_feature == "Face Detection":
            st.subheader("Detección de rostros:")
            if response.data.detected_faces:
                for idx, face in enumerate(response.data.detected_faces, start=1):
                    st.write(f"Rostro {idx}: confianza {round(face.confidence * 100, 2)}%")
            else:
                st.info("No se detectaron rostros en la imagen.")

        elif selected_feature == "Object Detection":
            st.subheader("Objetos detectados:")
            if response.data.image_objects:
                for obj in response.data.image_objects:
                    st.write(f"{obj.name} ({round(obj.confidence * 100, 2)}%)")
            else:
                st.info("No se detectaron objetos en la imagen.")

        elif selected_feature == "Image Classification":
            st.subheader("Clasificación de imagen:")
            if response.data.labels:
                for label in response.data.labels:
                    st.write(f"{label.name} ({round(label.confidence * 100, 2)}%)")
            else:
                st.info("No se encontraron categorías para esta imagen.")

    except Exception as e:
        st.error(f"Error: {e}")