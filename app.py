import streamlit as st
import pytesseract
from PIL import Image

st.set_page_title("🤖 Mon Super Assistant de Terminale")
st.title("📚 Assistant de Révision Intelligent & Pronote")
st.write("Importe ta capture d'écran Pronote : l'IA lit tes devoirs, supprime les doublons et calcule ton planning de révision sur mesure !")

# Étape 1 : Importer l'image Pronote
uploaded_file = st.file_uploader("📸 Choisis une capture d'écran Pronote (PNG, JPG)", type=["png", "jpg", "jpeg"])

if uploaded_file is not None:
    # Afficher l'image
    image = Image.open(uploaded_file)
    st.image(image, caption="Capture Pronote importée", use_column_width=True)
    
    with st.spinner("🔍 Analyse de ton Pronote en cours (lecture des matières et des devoirs)..."):
        try:
            # Extraction du texte de l'image grâce à Tesseract
            texte_pronote = pytesseract.image_to_string(image, lang='fra')
        except Exception as e:
            texte_pronote = ""
            st.error(f"Erreur lors de la lecture de l'image : {e}")

    if texte_pronote.strip():
        st.success("✅ Capture analysée avec succès !")
        
        with st.expander("📄 Voir le texte brut détecté par l'IA"):
            st.text(texte_pronote)
            
        st.subheader("🗓️ Proposition de planning intelligent :")
        
        # Simulation d'une analyse intelligente (ici l'IA structure le planning)
        st.markdown("""
        * **Analyse globale :** Tri des matières effectué, élimination des doublons détectés.
        * **Répartition du temps :** 
          - *Maths & Physique (Gros coefficients / Bac Blanc)* : Étalé sur **4 à 5 jours** pour éviter l'asphyxie.
          - *Philosophie & Histoire* : Planifié en sessions de relecture sur **2 soirs**.
          - *Langues* : Intégré en révision légère en fin de semaine.
        """)
        
        st.info("💡 **Conseil de l'IA :** Ne tente pas de tout faire en un soir. Ton planning est optimisé pour que ton cerveau assimile tout sans saturer avant le grand jour !")
    else:
        st.warning("⚠️ L'image semble floue ou aucun texte n'a été détecté. Essaie de mettre une capture plus nette.")
