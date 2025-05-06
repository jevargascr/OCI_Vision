# OCI Vision: Detección de Objetos con Python y Streamlit

Este tutorial te guiará paso a paso para construir una aplicación que utilice el servicio completo de **OCI Vision** usando **Python** y **Streamlit**. Analizaremos imágenes mediante clasificación, detección de objetos, detección de texto y detección de rostros.

---

## Servicios soportados

- **Image Classification**
- **Object Detection**
- **Text Detection**
- **Face Detection**

---

## 🔍 Requisitos Previos

- Tener una cuenta activa en Oracle Cloud (OCI).
- Compartimiento con permisos para Vision AI.
- Tener instalado Python 3.8+.
- Instalación de OCI CLI
- Tener creado un archivo de configuración de OCI en `~/.oci/config`.

---

## 🚀 1. Crear una VM en OCI

1. Ir a [Compute > Instances](https://cloud.oracle.com/compute/instances).
2. Crear una instancia Nombre: App_Vision
3. Sistema Operativo Oracle Linux 8.
4. Tipo sugerido para pruebas: `VM.Standard3.Flex`.
5. Configura el acceso SSH.

---

## 📁 2. Instalar dependencias

En la VM o tu entorno local:

Acceder por SSH
```bash
ssh -i <yourkey.pem> opc@<Public IP>
```

**Instalar herramientas para compilación de librerías como pyarrow:**

```bash
sudo dnf install git python38-pip -y
sudo dnf install -y gcc python3-devel
sudo pip3 install --upgrade pip setuptools wheel
pip3 install cython
```

**Luego instalar dependencias principales:**

```bash
pip3 install oci streamlit pillow pyarrow
```

**Configurar OCI CLI (si no lo has hecho):**

```bash
sudo dnf -y install oraclelinux-developer-release-el8
sudo dnf install python36-oci-cli
oci --version
oci setup config
oci os ns get
```

**Abrir el puerto 8501 en el firewall (Streamlit):**

```bash
sudo firewall-cmd --permanent --add-port=8501/tcp
sudo firewall-cmd --reload
```

---

## 📚 3. Crear la app en Python + Streamlit

```bash
cd $HOME
mkdir App
cd App
vi config.py
```

Archivo: `config.py`

```python
CONFIG_PATH = "~/.oci/config"
COMPARTMENT_ID = "ocid1.compartment.oc1..aaaaaaaadtvrqmyapdg5swh546q5ayxc6hlfxlwp2pbkxmk2yt2himsk7n6q"
MAX_RESULTS = 50
```

Archivo: `app.py`

```bash
vi app.py
```

```python
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
```

---

## 🔄 4. Ejecutar la aplicación

Flujo:
1. El usuario sube una imagen.
2. Selecciona el servicio de análisis.
3. La imagen se codifica y se envía a OCI Vision.
4. Se muestra el resultado en formato visual y texto amigable.

```bash
streamlit run app.py --server.port=8501
```

---

## 📊 5. Ejemplo de respuesta por servicio

- **Image Classification**
```json
{
  "labels": [
    { "name": "Cat", "confidence": 0.954 }
  ]
}
```

- **Object Detection**
```json
{
  "imageObjects": [
    { "name": "Traffic sign", "confidence": 0.95 }
  ]
}
```

- **Text Detection**
```json
{
  "imageText": {
    "lines": [
      { "text": "Menu", "confidence": 0.99 }
    ]
  }
}
```

- **Face Detection**
```json
{
  "detectedFaces": [
    { "confidence": 0.92, "qualityScore": 0.79 }
  ]
}
```

---

## 📊 6. Interpretación de campos clave por servicio

| Servicio            | Campo relevante       | Descripción                                 |
|---------------------|-----------------------|---------------------------------------------|
| Image Classification| `labels.name`         | Categoría reconocida en la imagen           |
| Object Detection    | `imageObjects.name`   | Objetos identificados con sus coordenadas   |
| Text Detection      | `imageText.lines.text`| Texto detectado línea por línea             |
| Face Detection      | `detectedFaces`       | Información de rostros y nivel de confianza |

---

---

## 💡 7. Arquitectura y herramientas utilizadas

Este proyecto demuestra cómo diferentes componentes tecnológicos trabajan en conjunto para ofrecer una solución de detección de objetos usando inteligencia artificial en la nube de Oracle.

Este proyecto utiliza:

- **Oracle Cloud Infrastructure (OCI)**: Proporciona el servicio de *Vision AI*, que permite detectar automáticamente objetos dentro de imágenes usando modelos preentrenados.
- **OCI Vision Service**: servicio de IA para analizar imágenes desde la nube Oracle.
- **Python SDK for OCI**: Permite interactuar con los servicios de OCI directamente desde código Python mediante llamadas autenticadas y estructuradas.
- **OCI CLI (Command Line Interface)**: Herramienta para configurar la conectividad, validar el acceso y realizar pruebas rápidas desde terminal.
- **Streamlit**: Framework ligero para construir interfaces web interactivas directamente desde Python, ideal para prototipos de AI y visualización de resultados.

### Servicios de OCI Vision incluidos:

- **Image Classification**: identifica automáticamente el contenido general de una imagen (por ejemplo, "perro", "auto", "paisaje"). Es útil para organización de fotos, etiquetado automático y moderación de contenido.

- **Object Detection**: detecta y localiza múltiples objetos dentro de una imagen, devolviendo su clase y ubicación. Es clave en aplicaciones como análisis de tráfico, conteo de inventario o monitoreo de seguridad.

- **Text Detection**: reconoce texto dentro de imágenes (impresas o manuscritas). Es fundamental para escaneo de documentos, recibos, carteles y reconocimiento automático de información estructurada.

- **Face Detection**: identifica rostros humanos en una imagen y proporciona características como puntuación de calidad y puntos faciales (ojos, boca, nariz). Tiene aplicaciones en autenticación, análisis de sentimientos y seguimiento en cámaras de seguridad.

Con estas herramientas, se crea una solución completa que:
1. Permite al usuario subir imágenes desde un navegador.
2. Codifica la imagen y la envía al modelo de IA en OCI.
3. Muestra los resultados de forma inmediata y accesible.

---

## 🎨 8. Ejemplo visual de la app funcionando

Incluye capturas como las siguientes:
- Imagen original subida.
- Lista de objetos detectados con porcentajes (sin volver a mostrar imagen).

---

## 📦 9. Estructura sugerida del repo GitHub

```
oci-object-detection/
├── app.py
├── requirements.txt
├── README.md
├── images/
│   ├── ejemplo_subida.png
│   └── resultado_deteccion.png
```