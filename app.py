import streamlit as st
import requests
import base64
from PIL import Image
import io
import json

# Configuration
API_BASE_URL = "http://localhost:8000"
AUTH_URL = "http://localhost:7000"

def get_auth_token(username: str, password: str) -> str:
    """Obtenir un token d'authentification"""
    try:
        response = requests.post(
            f"{AUTH_URL}/token",
            json={"username": username, "password": password}
        )
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            st.error("Erreur d'authentification")
            return None
    except Exception as e:
        st.error(f"Erreur de connexion: {e}")
        return None

def classify_document(file_content: bytes, file_type: str, token: str) -> dict:
    """Envoyer le document à l'API pour classification"""
    try:
        # Encoder le fichier en base64
        file_b64 = base64.b64encode(file_content).decode('utf-8')
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "content": file_b64,
            "file_type": file_type
        }
        
        response = requests.post(
            f"{API_BASE_URL}/predict",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erreur API: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        st.error(f"Erreur lors de la classification: {e}")
        return None

def main():
    st.set_page_config(
        page_title="Classification de Documents avec CLIP",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("📄 Classification de Documents avec CLIP")
    st.markdown("---")
    
    # Sidebar pour l'authentification
    with st.sidebar:
        st.header("🔐 Authentification")
        username = st.text_input("Nom d'utilisateur", value="admin")
        password = st.text_input("Mot de passe", type="password", value="admin")
        
        if st.button("Se connecter"):
            token = get_auth_token(username, password)
            if token:
                st.session_state.token = token
                st.success("✅ Connecté!")
            else:
                st.error("❌ Échec de la connexion")
    
    # Vérifier si l'utilisateur est connecté
    if "token" not in st.session_state:
        st.warning("⚠️ Veuillez vous connecter pour utiliser l'application")
        return
    
    # Interface principale
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.header("📁 Import de Document")
        
        uploaded_file = st.file_uploader(
            "Choisissez un document à classifier",
            type=['pdf', 'png', 'jpg', 'jpeg', 'txt', 'docx'],
            help="Formats supportés: PDF, images (PNG, JPG, JPEG), texte (TXT), Word (DOCX)"
        )
        
        if uploaded_file is not None:
            # Afficher les informations du fichier
            st.info(f"📄 Fichier: {uploaded_file.name} ({uploaded_file.size} bytes)")
            
            # Aperçu du fichier
            if uploaded_file.type.startswith('image/'):
                image = Image.open(uploaded_file)
                st.image(image, caption="Aperçu de l'image", use_column_width=True)
            
            # Bouton de classification
            if st.button("🔍 Classifier le Document", type="primary"):
                with st.spinner("Classification en cours..."):
                    file_content = uploaded_file.read()
                    result = classify_document(
                        file_content, 
                        uploaded_file.type, 
                        st.session_state.token
                    )
                    
                    if result:
                        st.success("✅ Classification terminée!")
                        
                        # Afficher les résultats
                        prediction = result.get("prediction", {})
                        st.subheader("📊 Résultats de Classification")
                        
                        col_pred, col_score = st.columns(2)
                        with col_pred:
                            st.metric("Type de Document", prediction.get("label", "N/A"))
                        with col_score:
                            st.metric("Score de Confiance", f"{prediction.get('score', 0):.2%}")
                        
                        # Détails JSON
                        with st.expander("🔍 Détails techniques"):
                            st.json(result)
    
    with col2:
        st.header("📈 Métriques en Temps Réel")
        
        # Afficher les métriques Prometheus
        try:
            metrics_response = requests.get(f"{API_BASE_URL}/metrics")
            if metrics_response.status_code == 200:
                metrics_text = metrics_response.text
                
                # Extraire les métriques importantes
                lines = metrics_text.split('\n')
                total_requests = 0
                avg_latency = 0
                
                for line in lines:
                    if 'clip_total_requests' in line and not line.startswith('#'):
                        try:
                            total_requests = float(line.split()[-1])
                        except:
                            pass
                    elif 'clip_request_latency_seconds_sum' in line and not line.startswith('#'):
                        try:
                            latency_sum = float(line.split()[-1])
                            if total_requests > 0:
                                avg_latency = latency_sum / total_requests
                        except:
                            pass
                
                st.metric("Total Requêtes", int(total_requests))
                st.metric("Latence Moyenne", f"{avg_latency:.3f}s")
                
            else:
                st.error("Impossible de récupérer les métriques")
                
        except Exception as e:
            st.error(f"Erreur métriques: {e}")
        
        st.markdown("---")
        st.markdown("🔗 **Liens Utiles:**")
        st.markdown("- [MLflow UI](http://localhost:5000)")
        st.markdown("- [Grafana Dashboard](http://localhost:3000)")
        st.markdown("- [Prometheus](http://localhost:9090)")
        st.markdown("- [API Docs](http://localhost:8000/docs)")

if __name__ == "__main__":
    main()
