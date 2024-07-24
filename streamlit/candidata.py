from io import BytesIO
import pandas as pd
from pypdf import PdfReader
import re
import streamlit as st

from match import match_jobs    # modul/fonction pour le chatbot qui va faire des recommandations


def main():

    ##### import des offres (csv) ####
    alljobs = pd.read_csv("candidata_v1_light.csv", sep=",")
    alljobs.sort_values(by="date_publication", ascending=False, inplace=True)
    alljobs.reset_index(drop=True, inplace=True)
    alljobs["lien"] = alljobs.apply(poste_avec_lien, axis=1)
    alljobs.drop(columns=["nom_emploi", "url"], inplace=True)
    alljobs.rename(columns={"lien": "poste"}, inplace=True)


    ##### import css #####
    with open('styles.css', 'r') as file:
        css = file.read()
    st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)


    ##### interface streamlit #####
    
    # introduction
    st.title("CandiData")

    st.write("\n")
    logos()
    st.write("\n")

    st.subheader("La Douceur de trouver son emploi")
    st.write("Trouver le job qui colle parfaitement à vos attentes.\
             Nous le faisons via des solutions innovantes qui vous permettent de trouver les offres d’emploi\
             qui se rapprochent le plus de votre profil.\
             Pas de profil type, juste l’envie d’évoluer dans le monde fascinant de la Data\
             et de vivre une expérience de recherche d’emploi nouvelle, simple et efficace.")
    st.write("\n")

    # boutons pour filtrer les offres
    autocomplete_ville = alljobs["ville"].unique().tolist()
    autocomplete_ville.sort()
    autocomplete_ville.insert(0, "Toutes les villes")

    autocomplete_contrat = alljobs["contrat"].unique().tolist()
    autocomplete_contrat.sort()
    autocomplete_contrat.insert(0, "Tous types de contrat")

    # j'utilise st.columns() pour les afficher dans la même ligne
    col1, col2 = st.columns(2)
    with col1:
        options_ville = st.selectbox(
            "Lieu de travail",
            options = autocomplete_ville,
            index = 0
        )
    with col2:
        options_contrat = st.selectbox(
            "Type de contrat",
            options = autocomplete_contrat,
            index = 0
        )
    
    # choix des offres les plus récentes avec ou sans filtres
    filtered_jobs = alljobs

    if options_ville != "Toutes les villes":
        filtered_jobs = filtered_jobs[filtered_jobs["ville"] == options_ville]
    
    if options_contrat != "Tous types de contrat":
        filtered_jobs = filtered_jobs[filtered_jobs["contrat"] == options_contrat]
    
    # initialisation du container qui va afficher les offres
    c = st.container()
    st.write("\n")

    # fonctionnalités llm pour affiner la recherche
    st.subheader("Personnaliser votre recherche")
    txt = st.text_area("Décrivez le poste de vos rêves", )
    if txt:
        # au cas où il y a une erreur avec le llm (trop de demandes, serveur inaccessible...)
        try:
            recommandations = match_jobs(txt)
            st.write(recommandations)
        except Exception:
            st.write("Désolé, nous sommes très chargés en ce moment. Veuillez relancer votre demande dans une minute.")
    

    # je transfrome le dataframe en objet HTML afin de pouvour afficher les liens (hyperlinks)
    # ...et j'ajoute un text au cas où aucune offre ne correspond aux filtres choisis pas l'utilisateur
    html_table = create_hyperlink_html(filtered_jobs)
    with c:
        if filtered_jobs.empty:
            st.write("Désolé, aucune offre ne correspond à vos critères.")
        else:
            st.markdown(html_table, unsafe_allow_html=True)
    
    st.write("\n")
    logos()


##### fonctions #####

# mettre lien dans l'intitulé du poste
def poste_avec_lien(job):
    lien = f"<a href={job['url']} target='_blank' class='custom-link'>{job['nom_emploi']}</a>"
    return lien

# fonction pour convertir le dataframe en objet HTML (pour avoir les liens vers les sites des offres)
def create_hyperlink_html(job):
    job = job[["poste", "nom_entreprise", "ville", "contrat"]]
    job.rename(columns={"poste": "Poste",
                        "nom_entreprise": "Entreprise",
                        "ville": "Ville",
                        "contrat": "Contrat"}, inplace=True)
    job = job.head(15)
    return job.to_html(escape=False, index=False)

# fonction pour afficher le logo (6 fois dans une ligne)
def logos():
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        st.image("logo.jpg")
    with col2:
        st.image("logo.jpg")
    with col3:
        st.image("logo.jpg")
    with col4:
        st.image("logo.jpg")
    with col5:
        st.image("logo.jpg")
    with col6:
        st.image("logo.jpg")



main()