import streamlit as st

st.set_page_config(
    page_title="Mon Super Assistant de Terminale",
    page_icon="🎓",
    layout="wide"
)

st.title("🎓 Mon Super Assistant de Terminale")
st.write("Bienvenue sur ton assistant personnel pour le Bac !")

# Menu de sélection dans la barre latérale
option = st.sidebar.selectbox(
    "Choisis une option :",
    ["Accueil", "Mathématiques", "Physique-Chimie", "Philosophie", "Annales & Révisions"]
)

if option == "Accueil":
    st.header("Page d'accueil")
    st.info("Sélectionne une option dans la barre latérale pour commencer à réviser.")
elif option == "Mathématiques":
    st.header("Section Mathématiques")
    st.write("Ici tu trouveras tes cours et exercices de maths.")
elif option == "Physique-Chimie":
    st.header("Section Physique-Chimie")
    st.write("Ici tu trouveras tes cours et exercices de physique-chimie.")
elif option == "Philosophie":
    st.header("Section Philosophie")
    st.write("Ici tu trouveras de l'aide pour la dissertation et les auteurs.")
elif option == "Annales & Révisions":
    st.header("Annales & Révisions")
    st.write("Prépare ton bac avec les sujets des années précédentes.")
