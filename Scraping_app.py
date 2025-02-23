import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup as bs
import base64
import streamlit.components.v1 as components


# Définition du background
def background(img):
    with open(img, "rb") as image:
        encoded = base64.b64encode(image.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp{{
            background-image: url("data:image/jpg;base64,{encoded}");
            background-size: contain;
            background-position: center;
            background-attachment: fixed;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )
background("Images\house9.avif") 

# Fonction de scraping pour les appartements
def apt_scraping(num_pages):
    data = []
    for page in range(num_pages):
        url = f'https://sn.coinafrique.com/categorie/appartements?page={page}'
        res = requests.get(url)
        contenu = bs(res.text, 'html.parser')
        appartements = contenu.find_all('div', class_='col s6 m4 l3')

        for apt in appartements:
            try:
                image_lien = 'https://sn.coinafrique.com/' + apt.find('img', class_='ad__card-img')['src']
                url_apt = 'https://sn.coinafrique.com/' + apt.find('a', class_='card-image ad__card-image waves-block waves-light')['href']
                
                recup = requests.get(url_apt)
                infos = bs(recup.text, 'html.parser')

                nombre_pieces = infos.find('span', class_='qt').text.strip()
                prix = infos.find('p', class_='price').text.strip().replace(' ','.').replace('.CFA','')
                adresse = infos.find('span', class_='valign-wrapper', attrs={"data-address": True}).text.strip()

                data.append({
                    'Nombre pièces': nombre_pieces,
                    'Prix (F CFA)': prix,
                    'Adresse': adresse,
                    'Lien Image': image_lien
                })
            except:
                pass
    
    return pd.DataFrame(data)

# Fonction de scraping pour les terrains
def terrains_scraping(num_pages):
    data = []
    for page in range(num_pages):
        url = f'https://sn.coinafrique.com/categorie/terrains?page={page}'
        res = requests.get(url)
        contenu = bs(res.text, 'html.parser')
        terrains = contenu.find_all('div', class_='col s6 m4 l3')

        for ter in terrains:
            try:
                image_lien = 'https://sn.coinafrique.com/' + ter.find('img', class_='ad__card-img')['src']
                url_ter = 'https://sn.coinafrique.com/' + ter.find('a', class_='card-image ad__card-image waves-block waves-light')['href']
                
                recup = requests.get(url_ter)
                infos = bs(recup.text, 'html.parser')

                superficie = infos.find('span', class_='qt').text.strip().replace('m²','').replace(' m2','').replace('m`','')
                prix = infos.find('p', class_='price').text.strip().replace(' ','.').replace('.CFA','')
                adresse = infos.find('span', class_='valign-wrapper', attrs={"data-address": True}).text.strip()

                data.append({
                    'Superficie (m²)': superficie,
                    'Prix (F CFA)': prix,
                    'Adresse': adresse,
                    'Lien Image': image_lien
                })
            except:
                pass
    
    return pd.DataFrame(data)

def telecharger(df, titre, cle):
    st.markdown("""<style>div.stButton {text-align: center}</style>""", unsafe_allow_html = True)
    if st.button(titre, cle):
        st.subheader('Dimension des données')
        st.write('Dimension: ' + str(df.shape[0]) + ' lignes et ' + str(df.shape[1]) + ' colonnes')
        st.dataframe(df)
        csv = df.to_csv(index=False).encode('utf-8')
        
        # Bouton de téléchargement avec le CSV
        st.download_button(label="Télécharger en CSV", data=csv, file_name=f"{titre.lower()}_scraping.csv", mime="text/csv")
 
# Interface Streamlit
st.markdown("<h1 style='text-align: center;'>Bienvenue sur la Plateforme de Scraping Immobilier !</h1>", unsafe_allow_html=True)
st.markdown("""
Cette application vous permet de collecter facilement des annonces immobilières (appartements et terrains) depuis le site CoinAfrique. Grâce à un simple clic, vous pouvez :
* **Scraper des annonces en choisissant le type de bien et le nombre de pages à explorer.**
* **Télécharger des données préexistantes pour les analyser.**
* **Évaluer l'application via un formulaire intégré.**
L'interface intuitive vous permet d'afficher et d'exporter les résultats en format CSV pour une exploitation ultérieure.
* **Librairies Python:** streamlit, pandas, requests, bs4
* **Source de données:** [Annonces appartemments à louer](https://sn.coinafrique.com/categorie/appartements) / [Annonces terrains à vendre](https://sn.coinafrique.com/categorie/terrains).
""")

# Contenu de la barre latérale
st.sidebar.title("Navigation")
choix = st.sidebar.radio("Que souhaitez-vous faire?", ["Scraper avec BeautifulSoup", "Télécharger des données", "Remplir le formulaire"])


if choix == "Scraper avec BeautifulSoup":
    st.markdown("<h3>Collectez des annonces immobilières en un clic !</h3>", unsafe_allow_html=True)
    
    # Choix du type de bien
    option = st.selectbox("Quel type de bien immobilier souhaitez-vous explorer aujourd'hui ?", ["Appartements", "Terrains"])
    
    # Choix du nombre de pages
    num_pages = st.number_input("Nombre de pages à scraper :", min_value=1, max_value=200, value=1)
    
    # Bouton de scraping
    if st.button("Lancer le scraping"):
        with st.spinner("Scraping en cours..."):
            if option == "Appartements":
                df = apt_scraping(num_pages)
                
            else:
                df = terrains_scraping(num_pages)
            
            if not df.empty:
                st.success("Scraping terminé avec succès !")
                st.dataframe(df)

            # Bouton de téléchargement
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(label="Télécharger en CSV", data=csv, file_name=f"{option.lower()}_scraping.csv", mime="text/csv")

elif choix == "Télécharger des données":
    st.write("### Que souhaitez-vous télécharger ?")
    Appartemments_csv = pd.read_csv("Web_scraper_data\Apartements_scraping.csv")
    Terrains_csv = pd.read_csv("Web_scraper_data\Terrains_Scrape.csv")
    st.markdown(""" <style> .stButton>button {
            font-size: 10px;
            height: 2em;
            width: 20em;
            } </style>""", unsafe_allow_html = True) 
# Chargement des fichiers CSV si fournis
    if Appartemments_csv is not None:
        telecharger(Appartemments_csv, "Appartemments", 1)

    if Terrains_csv is not None:
        telecharger(Terrains_csv, "Terrains", 2)
    
else:
    choix_2 = st.selectbox("Choisissez le formulaire à remplir :", 
                       ["Formulaire KoBoToolbox", "Formulaire Google Forms"])

    # Affichage du formulaire en fonction du choix
    if choix_2 == "Formulaire KoBoToolbox":
        components.html("""
        <iframe src="https://ee.kobotoolbox.org/x/GTkDEqM6" width="800" height="1100"></iframe>
        """, height=1100, width=800)
    elif choix_2 == "Formulaire Google Forms":
        components.html("""
        <iframe src="https://docs.google.com/forms/d/e/1FAIpQLScr7akh1hC0G6lil1eZoNFLo68__Or1t4T7UxV3OZc84dJVqA/viewform?usp=dialog" width="800" height="1100"></iframe>
        """, height=1100, width=800)
    