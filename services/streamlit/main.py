import streamlit as st
import requests
import plotly.graph_objects as go
from PIL import Image
import numpy as np

# URLs
AUTH_URL = "http://dsdc-auth:8000/token"
API_URL = "http://dsdc-predict:8000/v1/predict"

# Classes
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

def get_token(username, password):
    response = requests.post(
        AUTH_URL,
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    if response.status_code == 200:
        return response.json().get("access_token")
    else:
        return None

# Config Streamlit
st.set_page_config(
    page_title="Document Classifier",
    layout="wide",
    menu_items={
        "About": None,
        "Get help": None,
        "Report a bug": None
    }
)

# Sidebar login form
st.sidebar.title("Connexion")
with st.sidebar.form(key="login_form"):
    username = st.text_input("Login")
    password = st.text_input("Password", type="password")
    login_button = st.form_submit_button("Login")
token = None
if login_button:
    token = get_token(username, password)
    if token:
        st.sidebar.success("Successfully logged in!")
        st.session_state["token"] = token
    else:
        st.sidebar.error("Wrong login or password")
if "token" in st.session_state:
    token = st.session_state["token"]

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

    if token is None:
        st.error("Pleas log-in before using the service")
    else:
        files = {
            "image": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
        }
        headers = {"Authorization": f"Bearer {token}"}

        with st.spinner("Sending image to prediction API..."):
            try:
                response = requests.post(API_URL, files=files, headers=headers)
                response.raise_for_status()
                result = response.json()
            except Exception as e:
                st.error(f"Error calling the API: {e}")
                st.stop()
        label_index = result["label"]
        probas = result["probas"]
        predicted_class = CLASS_NAMES[label_index]
        max_entropy = np.log(len(probas))
        ent = entropy(probas)
        confidence_pct = int((1 - ent / max_entropy) * 100)
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
