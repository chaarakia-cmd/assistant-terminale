import streamlit as st
import google.generativeai as genai
from PIL import Image
import datetime

# Configuration de la page
st.set_page_config(
    page_title="Mon Assistant de Terminale - Complet & Intelligent",
    page_icon="🎓",
    layout="wide"
)

# --- MENU LATÉRAL ---
st.sidebar.title("📚 Navigation")
menu = st.sidebar.selectbox(
    "Choisir une option :",
    [
        "📅 Ce qu'il faut faire aujourd'hui", 
        "🗓️ Agenda Annuel (Toutes les semaines)", 
        "📸 IA & Analyse Pronote (Planning intelligent)", 
        "📖 Manuel & Cours", 
        "🎓 Parcoursup", 
        "📂 Suivi par matières", 
        "🎤 Grand Oral"
    ]
)

# Configuration de la clé API pour l'IA dans la barre latérale
st.sidebar.markdown("---")
st.sidebar.subheader("🔑 Connexion IA (Gemini)")
api_key = st.sidebar.text_input("Entre ta clé API Google Gemini :", type="password")
st.sidebar.markdown("[Obtenir une clé gratuite sur Google AI Studio](https://aistudio.google.com/)")

# --- 1. ACCUEIL : CE QU'IL FAUT FAIRE AUJOURD'HUI ---
if menu == "📅 Ce qu'il faut faire aujourd'hui":
    st.title("🎯 Au programme aujourd'hui")
    st.write("Voici ta charge de travail du jour, calculée pour respecter tes limites (max 2h30 en semaine avec marge).")
    st.info("💡 Astuce : Importe ta capture Pronote dans l'onglet dédié pour que l'IA remplisse ton agenda automatiquement !")

# --- 2. AGENDA ANNUEL (VISIBILITÉ SUR TOUTE L'ANNÉE) ---
elif menu == "🗓️ Agenda Annuel (Toutes les semaines)":
    st.title("🗓️ Agenda Complet de l'Année")
    st.write("Visualise toutes les semaines de ton année scolaire, même pour les devoirs prévus dans plusieurs mois.")

    # Génération d'une vue par semaines sur plusieurs mois (ex: 36 semaines de l'année scolaire)
    date_debut = datetime.date(2026, 9, 1) # Début d'année scolaire type
    
    col1, col2 = st.columns([1, 2])
    with col1:
        semaine_selectionnee = st.selectbox(
            "Choisis une semaine à consulter :",
            [f"Semaine {i} (À partir du {date_debut + datetime.timedelta(weeks=i-1)})" for i in range(1, 40)]
        )
    
    with col2:
        st.subheader(f"📌 Détails pour : {semaine_selectionnee}")
        st.markdown("""
        * **Lundi :** Rien de prévu pour l'instant (ou charge légère)
        * **Mardi :** Exercice de Maths (fait en 1 soirée)
        * **Mercredi :** Fiches de révision Philosophie
        * **Jeudi :** -
        * **Vendredi :** -
        * **Week-end (3-4h max + 1h marge) :** Avancée sur le projet de Spé / Grand Oral.
        """)
    
    st.markdown("---")
    st.write("🔍 *Tu peux anticiper n'importe quel devoir ou DS à venir dans 1 mois, 2 mois ou 4 mois grâce à cette vue globale.*")

# --- 3. IA & ANALYSE PRONOTE (AVEC VRAI RAISONNEMENT) ---
elif menu == "📸 IA & Analyse Pronote (Planning intelligent)":
    st.title("🤖 Planificateur IA Intelligent (Pronote & Contraintes)")
    st.markdown("""
    **Règles strictes intégrées à l'IA :**
    * 🛑 **Anti-doublons & Lecture d'image :** Analyse des matières et suppression des doublons.
    * ⏰ **Gestion du temps :** Max **2h30 en semaine** (2h + 30 min de marge), **3 à 4h le week-end** (avec 1h de marge).
    * 🧠 **Répartition sur-mesure :** 
      - Un exercice simple = fait en **une seule soirée** (pas d'étalement inutile).
      - Pas de report absurde d'un devoir lointain sur un soir déjà plein.
      - Découpage des chapitres de DS selon **leur nombre réel de parties** (1, 2, 4...).
      - Révision générale placée **idéalement la veille ou 2 jours avant le DS** (et jusqu'à 3 jours avant maximum en cas de saturation).
    """)

    uploaded_file = st.file_uploader("📸 Importe ta capture d'écran Pronote (PNG, JPG)", type=["png", "jpg", "jpeg"])

    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption="Capture Pronote importée", use_column_width=True)

        if st.button("🚀 Lancer l'analyse intelligente et générer l'agenda"):
            if not api_key:
                st.error("⚠️ Merci d'entrer ta clé API Gemini dans la barre latérale à gauche pour activer l'intelligence artificielle !")
            else:
                with st.spinner("L'IA analyse ton image, supprime les doublons et structure ton planning selon tes règles de temps..."):
                    try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        
                        prompt = """
                        Agis en tant qu'assistant de révision expert et intelligent pour un élève de Terminale. 
                        Analyse cette capture d'écran Pronote en respectant scrupuleusement ces règles de logique :
                        1. Extrais les devoirs, exercices et DS en éliminant proprement les doublons.
                        2. Respecte les limites de temps strictes : max 2h30 par soir en semaine (2h + 30 min de marge) et 3 à 4h le week-end (avec 1h de marge).
                        3. Pour les exercices simples : planifie-les sur une seule et unique soirée adaptée, sans les étaler bêtement sur plusieurs jours. Ne surcharge pas un soir si un devoir lointain peut être placé sur un jour plus creux ou le week-end.
                        4. Pour les DS et chapitres : analyse le volume ou le type de chapitre. Ne fais pas un découpage fixe à 4 parties par défaut : adapte le nombre de sessions de révision au nombre réel de parties du chapitre (qu'il y en ait 1, 2 ou plus).
                        5. Pour la révision finale du DS : place-la idéalement la veille ou 2 jours avant le DS. N'utilise le délai de 3 jours avant qu'en cas de saturation absolue des soirs juste avant.
                        Donne un planning clair, structuré et intelligent, rédigé entièrement en français.
                        """
                        
                        response = model.generate_content([prompt, image])
                        
                        st.success("✅ Planning intelligent généré avec succès par l'IA !")
                        st.markdown(response.text)
                        
                    except Exception as e:
                        st.error(f"Une erreur est survenue lors de la communication avec l'IA : {e}")

# --- 4. MANUEL & COURS ---
elif menu == "📖 Manuel & Cours":
    st.title("📖 Manuel & Cours de Terminale")
    st.write("Retrouve ici tes cours structurés par chapitres.")

# --- 5. PARCOURSUP ---
elif menu == "🎓 Parcoursup":
    st.title("🎓 Espace Parcoursup")
    st.write("Suivi de tes voeux, de tes lettres de motivation et du calendrier.")

# --- 6. SUIVI PAR MATIÈRES ---
elif menu == "📂 Suivi par matières":
    st.title("📂 Devoirs et révisions par matières")
    st.write("Fais le point matière par matière (Maths, Physique, Philo, etc.).")

# --- 7. GRAND ORAL ---
elif menu == "🎤 Grand Oral":
    st.title("🎤 Préparation du Grand Oral")
    st.write("Suivi de tes deux questions, de ton argumentaire et de ta soutenance.")
