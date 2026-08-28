import streamlit as st

st.title("📚 Mon Assistant de Terminale")
st.write("Bienvenue sur mon application de révision !")

# Un petit test pour voir si tout marche
nom = st.text_input("Comment tu t'appelles ?")
if nom:
    st.success(f"Enchanté {nom} ! C'est parti pour le succès au Bac !")
