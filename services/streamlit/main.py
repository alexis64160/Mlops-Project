import streamlit as st
import requests
import plotly.graph_objects as go
from PIL import Image
import numpy as np

# API endpoint
API_URL = "http://dsdc_predict:8000/v1/predict"

# DVL-CDIP class labels
CLASS_NAMES = [
    "Letter", "Form", "Email", "Handwritten", "Advertisement",
    "Scientific report", "Scientific publication", "Specification",
    "File folder", "News article", "Budget", "Invoice",
    "Presentation", "Questionnaire", "Resume", "Memo"
]

def entropy(probas):
    probas = np.array(probas)
    eps = 1e-12
    probas = np.clip(probas, eps, 1.0)
    ent = -np.sum(probas * np.log(probas))
    return ent

# Streamlit config (remove Deploy menu)
st.set_page_config(
    page_title="Document Classifier",
    layout="wide",
    menu_items={
        "About": None,
        "Get help": None,
        "Report a bug": None
    }
)

st.title("Document Classification Interface")

uploaded_file = st.file_uploader("Upload an image (JPEG, PNG, TIFF)", type=["jpg", "jpeg", "png", "tiff"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)

    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("#### Uploaded Image")
        st.image(image, use_container_width=True)

        st.markdown("""
            <style>
            img {
                max-height: 600px !important;
            }
            </style>
        """, unsafe_allow_html=True)

    files = {
        "image": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
    }

    with st.spinner("Sending image to prediction API..."):
        try:
            response = requests.post(API_URL, files=files)
            response.raise_for_status()
            result = response.json()
        except Exception as e:
            st.error(f"Error calling the API: {e}")
            st.stop()

    label_index = result["label"]
    probas = result["probas"]
    predicted_class = CLASS_NAMES[label_index]

    # Compute confidence via entropy
    max_entropy = np.log(len(probas))
    ent = entropy(probas)
    confidence_pct = int((1 - ent / max_entropy) * 100)

    # Color based on confidence
    if confidence_pct >= 85:
        color = "green"
    elif confidence_pct >= 60:
        color = "orange"
    else:
        color = "red"

    with col2:
        st.markdown(f"""
            <h2 style='color: {color};'>
                {predicted_class}
                <span style='font-size: 0.7em; color: grey;'>(confidence={confidence_pct}%)</span>
            </h2>
        """, unsafe_allow_html=True)

        # Push chart down to bottom
        st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)

        confidence_percent = [p * 100 for p in probas]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=CLASS_NAMES,
            y=confidence_percent,
            hoverinfo="x+y",
            marker_color='lightskyblue'
        ))

        fig.update_layout(
            height=400,
            margin=dict(l=10, r=10, t=10, b=80),
            yaxis_title="Predict proba (%)",
            yaxis=dict(range=[0, 100]),
            showlegend=False
        )

        fig.update_xaxes(showticklabels=False)

        st.plotly_chart(fig, use_container_width=True)
