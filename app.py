import streamlit as st
import json
import os
import time
import uuid
from datetime import datetime, date, timedelta
from PIL import Image
import google.generativeai as genai

st.set_page_config(
    page_title="Mon Assistant de Terminale",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Indique au navigateur que la page est en français
st.markdown('<html lang="fr"></html>', unsafe_allow_html=True)

DATA_FILE = "devoirs_data.json"

# --- CHARGEMENT & SAUVEGARDE ---
def charger_donnees():
    structure_defaut = {
        "devoirs": [],
        "dossiers_matieres": {
            "📐 Spé Maths": [],
            "🧪 Spé Physique-Chimie": [],
            "🔢 Option Maths Expertes": [],
            "🧠 Philosophie": [],
            "📜 Histoire-Géo": [],
            "🔬 Enseignement Scientifique": [],
            "🇬🇧 Anglais (LVA)": [],
            "🇪🇸 Espagnol (LVB)": [],
            "🏃 EPS": [],
            "⚖️ EMC": [],
            "🎓 Grand Oral": [],
            "📝 Bac Blanc": [],
            "📌 Autre": []
        },
        "parcoursup": [],
        "grand_oral": {"q1_titre": "", "q1_plan": "", "q2_titre": "", "q2_plan": ""}
    }
    
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    for cle in structure_defaut:
                        if cle not in data:
                            data[cle] = structure_defaut[cle]
                    
                    for v in data.get("parcoursup", []):
                        if "id" not in v:
                            v["id"] = str(uuid.uuid4())
                            
                    return data
                elif isinstance(data, list):
                    structure_defaut["devoirs"] = data
                    return structure_defaut
        except Exception:
            return structure_defaut
    return structure_defaut

def sauvegarder_donnees():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.app_data, f, ensure_ascii=False, indent=4)

if "app_data" not in st.session_state:
    st.session_state.app_data = charger_donnees()

# --- ALGORITHME IA : ANALYSE ET ÉTALEMENT INTELLIGENT ---
def IA_analyser_et_etaler(description, matiere, date_echeance_str):
    desc_lower = description.lower()
    
    mots_lourds = ["bac blanc", "ds", "dm", "dme", "chapitre", "synthèse", "grand oral", "contrôle"]
    etoiles = 2
    if any(m in desc_lower for m in mots_lourds):
        etoiles += 2
        
    date_echeance = datetime.strptime(str(date_echeance_str), "%Y-%m-%d").date()
    aujourdhui = date.today()
    jours_restants = max(1, (date_echeance - aujourdhui).days)

    if jours_restants <= 2:
        etoiles += 1
    etoiles = min(5, max(1, etoiles))

    fichiers_cours = st.session_state.app_data["dossiers_matieres"].get(matiere, [])
    nb_fichiers = len(fichiers_cours)

    # Si c'est un simple exercice, 1 seule séance
    if "exo" in desc_lower or "exercice" in desc_lower or etoiles <= 2:
        nb_seances = 1
    else:
        nb_seances = 3 if etoiles >= 3 and jours_restants >= 3 else (2 if jours_restants >= 2 else 1)
        
    pas = max(1, jours_restants // nb_seances)
    
    seances = []
    curr = aujourdhui
    for i in range(nb_seances):
        if curr <= date_echeance:
            info_ext = f" (Inclus {nb_fichiers} cours du dossier)" if nb_fichiers > 0 else ""
            seances.append({
                "date": str(curr),
                "detail": f"Séance {i+1}/{nb_seances}{info_ext}"
            })
            curr += timedelta(days=pas)

    return etoiles, seances

# --- NAVIGATION LATÉRALE ---
st.sidebar.title("🎓 Mon Espace Terminale")
menu = st.sidebar.radio("Menu :", [
    "🗓️ Agenda & Planning de l'App",
    "📷 Importer Capture Pronote (IA Gemini)",
    "➕ Ajouter Devoir / Révision (IA)",
    "📂 Dossiers Matériels & Bac Blanc",
    "🎯 Suivi Parcoursup",
    "🎤 Espace Grand Oral"
])

# CLE API GEMINI
st.sidebar.divider()
st.sidebar.subheader("🔑 Clé API Gemini (Gratuite)")
api_key = st.sidebar.text_input("Colle ta clé API Gemini :", type="password", key="gemini_key")
st.sidebar.caption("[Obtenir une clé gratuite sur Google AI Studio](https://aistudio.google.com/)")

# BOUTON JOKER
st.sidebar.divider()
st.sidebar.subheader("🛟 Urgence Fatigué")
if st.sidebar.button("😴 BOUTON JOKER : Soirée KO !", use_container_width=True):
    demain = str(date.today() + timedelta(days=1))
    for d in st.session_state.app_data["devoirs"]:
        if not d.get("fait", False):
            d["date_limite"] = demain
            if "seances" in d:
                for s in d["seances"]:
                    if s["date"] == str(date.today()):
                        s["date"] = demain
    sauvegarder_donnees()
    st.sidebar.success("Toutes tes tâches du soir sont décalées à demain !")
    st.rerun()

# --- 1. AGENDA INTÉGRÉ ---
if menu == "🗓️ Agenda & Planning de l'App":
    st.title("🗓️ Mon Agenda Intégré")
    
    devoirs = st.session_state.app_data["devoirs"]
    aujourdhui_str = str(date.today())
    
    taches_soir = [d for d in devoirs if not d.get("fait", False) and 
                   (d.get("date_limite") == aujourdhui_str or any(s["date"] == aujourdhui_str for s in d.get("seances", [])))]
    total_etoiles = sum(d["etoiles"] for d in taches_soir)

    col_m, col_p = st.columns(2)
    with col_m:
        st.subheader("📊 Météo du soir")
        if not taches_soir:
            st.success("🟢 Aucune révision prévue ce soir !")
        elif total_etoiles <= 4:
            st.success(f"🟢 Soirée Tranquille — {total_etoiles} ⭐ (Charge respectée : < 2h30)")
        elif total_etoiles <= 8:
            st.info(f"🟡 Soirée Standard — {total_etoiles} ⭐ (Environ 2h - 2h30)")
        else:
            st.warning(f"🟠 Grosse Soirée — {total_etoiles} ⭐ (Attention au dépassement)")

    with col_p:
        st.subheader("⏱️ Minuteur Focus")
        c1, c2 = st.columns([1, 1])
        with c1:
            mins = st.number_input("Minutes", 1, 120, 25, label_visibility="collapsed")
        with c2:
            lancer = st.button("🚀 Lancer", use_container_width=True)
        
        if lancer:
            total_sec = mins * 60
            barre = st.progress(0)
            texte_chrono = st.empty()
            
            for s in range(total_sec, -1, -1):
                m, sec = divmod(s, 60)
                texte_chrono.markdown(f"### ⏳ **{m:02d}:{sec:02d}**")
                barre.progress((total_sec - s) / total_sec)
                time.sleep(1)
                
            texte_chrono.markdown("### 🎉 **Session terminée !**")
            st.balloons()

    st.divider()

    tab_jour, tab_semaine, tab_annee = st.tabs(["📅 Vue Jour par Jour", "🗓️ Planning 7 Jours", "📅 Vision Globale (Année)"])

    with tab_jour:
        date_sel = st.date_input("Consulter le calendrier à la date du :", date.today())
        date_sel_str = str(date_sel)
        st.subheader(f"Programme du {date_sel.strftime('%d/%m/%Y')}")

        taches_trouvees = []
        for d in devoirs:
            est_rendu = d.get("date_limite") == date_sel_str
            seance_match = next((s for s in d.get("seances", []) if s["date"] == date_sel_str), None)
            if est_rendu or seance_match:
                taches_trouvees.append((d, est_rendu, seance_match))

        if not taches_trouvees:
            st.info("Aucune tâche ni révision planifiée pour ce jour.")
        else:
            for idx, (d, est_rendu, seance) in enumerate(taches_trouvees):
                badge = "🎯 RENDU FINAL" if est_rendu else f"📖 {seance['detail']}"
                st.markdown(f"### {badge} : [{d['matiere']}] {d['description']}")
                st.caption(f"Difficulté : {'⭐'*d['etoiles']} | Rendu final : {d.get('date_limite')}")
                
                col1, col2 = st.columns(2)
                with col1:
                    lbl = "Marquer À faire" if d.get("fait") else "Marquer Fait ✔️"
                    if st.button(lbl, key=f"vj_f_{idx}_{d['description']}"):
                        d["fait"] = not d.get("fait", False)
                        sauvegarder_donnees()
                        st.rerun()
                with col2:
                    if st.button("🗑️ Supprimer", key=f"vj_d_{idx}_{d['description']}"):
                        st.session_state.app_data["devoirs"].remove(d)
                        sauvegarder_donnees()
                        st.rerun()
                st.divider()

    with tab_semaine:
        st.subheader("Visualisation des 7 prochains jours")
        jours = [date.today() + timedelta(days=i) for i in range(7)]
        cols = st.columns(7)
        for i, j_date in enumerate(jours):
            j_str = str(j_date)
            with cols[i]:
                st.markdown(f"**{j_date.strftime('%a %d/%m')}**")
                st.divider()
                count = 0
                for d in devoirs:
                    in_seance = any(s["date"] == j_str for s in d.get("seances", []))
                    in_rendu = d.get("date_limite") == j_str
                    if in_seance or in_rendu:
                        icon = "🎯" if in_rendu else "📖"
                        st.caption(f"{'✔️' if d.get('fait') else '📌'} {icon} **{d['matiere']}**")
                        st.text(d['description'][:15] + "...")
                        count += 1
                if count == 0:
                    st.caption("Libre")

    with tab_annee:
        st.subheader(" Vision Globale des semaines de l'année")
        semaine_offset = st.slider("Sélectionner une semaine dans l'année (S+1 à S+40) :", 1, 40, 1)
        target_date = date.today() + timedelta(weeks=semaine_offset)
        st.write(f"**Échéances prévues autour du {target_date.strftime('%d/%m/%Y')} :**")
        
        trouve_futur = False
        for d in devoirs:
            d_date = datetime.strptime(d.get("date_limite"), "%Y-%m-%d").date()
            if abs((d_date - target_date).days) <= 3:
                st.write(f"- 📌 **[{d['matiere']}]** {d['description']} (Date de rendu : {d['date_limite']})")
                trouve_futur = True
        if not trouve_futur:
            st.info("Aucune grosse échéance enregistrée pour cette période.")

# --- 2. IMPORT CAPTURE PRONOTE (IA GEMINI INTÉGRÉE) ---
elif menu == "📷 Importer Capture Pronote (IA Gemini)":
    st.title("📷 Importation & Analyse Intelligent par Capture Pronote")
    st.write("Dépose ici ta capture d'écran Pronote. L'IA analyse l'image, filtre les doublons et organise ton travail selon tes limites.")

    fichier_image = st.file_uploader("Sélectionner la capture Pronote (PNG, JPG)", type=["png", "jpg", "jpeg"])
    matieres = list(st.session_state.app_data["dossiers_matieres"].keys())

    if fichier_image:
        image = Image.open(fichier_image)
        st.image(image, caption="Capture chargée", use_container_width=True)
        
        c1, c2 = st.columns(2)
        with c1:
            matiere_sel = st.selectbox("Matière concernée", matieres)
            type_import = st.radio("Type de document", ["Devoir / DS à faire", "Cours / Chapitre à classer"])
        with c2:
            date_echeance = st.date_input("Date de rendu / Examen", date.today() + timedelta(days=3))

        if st.button("🚀 Analyser avec l'IA Gemini et enregistrer", use_container_width=True):
            if not api_key:
                st.error("⚠️ Merci d'entrer ta clé API Gemini dans le menu latéral à gauche !")
            else:
                with st.spinner("L'IA Gemini analyse l'image, supprime les doublons et évalue la charge..."):
                    try:
                        genai.configure(api_key=api_key)
                        model = genai.GenerativeModel('gemini-1.5-flash')
                        
                        prompt = f"""
                        Analyse cette capture Pronote pour un élève de Terminale.
                        1. Extrais le texte exact des devoirs ou cours sans doublons.
                        2. Respecte les limites de temps : max 2h30 par soir en semaine (avec 30 min de marge) et 3 à 4h le week-end.
                        3. Si c'est un simple exercice, mets-le sur une seule soirée adaptée.
                        4. Si c'est un DS, adapte la révision au nombre réel de parties du chapitre et place la révision finale idéalement la veille ou 2 jours avant.
                        Donne une description synthétique et claire en français.
                        """
                        response = model.generate_content([prompt, image])
                        texte_analyse = response.text

                        st.markdown("### 🤖 Résultat de l'analyse IA :")
                        st.write(texte_analyse)

                        if type_import == "Devoir / DS à faire":
                            etoiles, seances = IA_analyser_et_etaler(texte_analyse, matiere_sel, str(date_echeance))
                            st.session_state.app_data["devoirs"].append({
                                "matiere": matiere_sel,
                                "description": texte_analyse[:100] + "...",
                                "etoiles": etoiles,
                                "fait": False,
                                "date_limite": str(date_echeance),
                                "seances": seances
                            })
                            sauvegarder_donnees()
                            st.success("✅ Devoir analysé par l'IA et ajouté dans ton agenda !")
                        else:
                            st.session_state.app_data["dossiers_matieres"][matiere_sel].append({
                                "titre": f"Import IA - {date.today().strftime('%d/%m')}",
                                "contenu": texte_analyse,
                                "date_ajout": str(date.today())
                            })
                            sauvegarder_donnees()
                            st.success(f"✅ Cours analysé et classé dans le dossier {matiere_sel} !")

                    except Exception as e:
                        st.error(f"Erreur lors de l'analyse IA : {e}")

# --- 3. AJOUT MANUEL (IA) ---
elif menu == "➕ Ajouter Devoir / Révision (IA)":
    st.title("🤖 Ajout Manuel & Découpage IA")
    matieres = list(st.session_state.app_data["dossiers_matieres"].keys())

    with st.form("form_ia"):
        c1, c2 = st.columns(2)
        with c1:
            matiere = st.selectbox("Matière", matieres)
            description = st.text_input("Description (ex: Exo 45 p 102 ou DS Chapitre 2)")
        with c2:
            date_echeance = st.date_input("Date de rendu / Examen", date.today() + timedelta(days=4))
        
        submitted = st.form_submit_button("🤖 Générer et Étaler")

    if submitted and description:
        etoiles, seances = IA_analyser_et_etaler(description, matiere, str(date_echeance))
        st.session_state.app_data["devoirs"].append({
            "matiere": matiere,
            "description": description,
            "etoiles": etoiles,
            "fait": False,
            "date_limite": str(date_echeance),
            "seances": seances
        })
        sauvegarder_donnees()
        st.success("Tâche ajoutée et planifiée !")
        st.rerun()

# --- 4. DOSSIERS MATÉRIELS & ARCHIVES BAC BLANC ---
elif menu == "📂 Dossiers Matériels & Bac Blanc":
    st.title("📂 Dossiers de Révision & Prépa Bac Blanc")

    st.subheader("📚 Consultation des cours enregistrés")
    matieres = list(st.session_state.app_data["dossiers_matieres"].keys())
    mat_sel = st.selectbox("Sélectionner la matière à réviser", matieres)
    
    docs = st.session_state.app_data["dossiers_matieres"].get(mat_sel, [])
    if docs:
        for idx, d in enumerate(docs):
            with st.expander(f"📄 {d['titre']} (Ajouté le {d['date_ajout']})"):
                st.write(d["contenu"])
    else:
        st.info("Aucun cours enregistré pour cette matière.")

    st.divider()
    st.subheader("📝 Récapitulatif de révision pour le Bac Blanc")
    for mat, liste_docs in st.session_state.app_data["dossiers_matieres"].items():
        if liste_docs:
            st.markdown(f"#### 📘 {mat}")
            for doc in liste_docs:
                st.checkbox(f"Révisé : {doc['titre']}", key=f"bb_chk_{mat}_{doc['titre']}")

# --- 5. PARCOURSUP TRACKER ---
elif menu == "🎯 Suivi Parcoursup":
    st.title("🎯 Suivi des Vœux Parcoursup")

    with st.form("form_p"):
        voeu = st.text_input("Nom de la formation / École / CPGE")
        if st.form_submit_button("Ajouter ce vœu") and voeu:
            st.session_state.app_data["parcoursup"].append({
                "id": str(uuid.uuid4()),
                "voeu": voeu,
                "projet_motive": False,
                "pieces": False,
                "confirme": False
            })
            sauvegarder_donnees()
            st.rerun()

    st.divider()
    voeux = st.session_state.app_data["parcoursup"]
    a_supprimer = None

    for v in voeux:
        vid = v.get("id", str(uuid.uuid4()))
        st.subheader(f"🎓 {v['voeu']}")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            v["projet_motive"] = st.checkbox("Projet Motivé", value=v["projet_motive"], key=f"pm_{vid}")
        with c2:
            v["pieces"] = st.checkbox("Pièces jointes OK", value=v["pieces"], key=f"pj_{vid}")
        with c3:
            v["confirme"] = st.checkbox("Confirmé ✔️", value=v["confirme"], key=f"conf_{vid}")
        with c4:
            if st.button("🗑️ Supprimer", key=f"del_p_{vid}"):
                a_supprimer = v

        st.divider()

    if a_supprimer:
        st.session_state.app_data["parcoursup"].remove(a_supprimer)
        sauvegarder_donnees()
        st.rerun()

# --- 6. ESPACE GRAND ORAL ---
elif menu == "🎤 Espace Grand Oral":
    st.title("🎤 Préparation au Grand Oral")
    go = st.session_state.app_data["grand_oral"]

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("📌 Question 1")
        go["q1_titre"] = st.text_input("Sujet Q1", value=go.get("q1_titre", ""))
        go["q1_plan"] = st.text_area("Plan Q1", value=go.get("q1_plan", ""), height=150)
    with c2:
        st.subheader("📌 Question 2")
        go["q2_titre"] = st.text_input("Sujet Q2", value=go.get("q2_titre", ""))
        go["q2_plan"] = st.text_area("Plan Q2", value=go.get("q2_plan", ""), height=150)

    if st.button("💾 Sauvegarder mes fiches Grand Oral"):
        sauvegarder_donnees()
        st.success("Fiches enregistrées !")

    st.divider()
    st.subheader("⏱️ Chronomètre officiel (20 minutes)")
    if st.button("🚀 Démarrer la simulation (20 min)"):
        total_sec_go = 20 * 60
        barre_go = st.progress(0)
        chrono_go = st.empty()
        for s in range(total_sec_go, -1, -1):
            m, sec = divmod(s, 60)
            chrono_go.markdown(f"### ⏳ Temps restant : **{m:02d}:{sec:02d}**")
            barre_go.progress((total_sec_go - s) / total_sec_go)
            time.sleep(1)
        chrono_go.markdown("### 🎉 **Temps écoulé !**")
        st.balloons()
