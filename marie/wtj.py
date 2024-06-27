from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random
from datetime import date
from datetime import datetime

import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import re

import numpy as np

##############  PROCEDURE GENERALE ####################################
# 1. Aller sur la page de résultats avec selenium
# 2. Récupérer les URL pour aller de page en page
# 3. Faire une fonction pour aller récupérer les URL de chaque annonce sur chaque page
# 4. Couper les URL en relatif puis les reconcatener pour les passer dans l'API
# 5. Itérer pour requêter l'API avec chaque URL récupérée sur chaque page de résultats
# 6. Transformer en dataframe, décompacter et dropper ce qui doit l'être
# 7. Nettoyer les données, renommer et réordonner les colonnes
# 7. Exporter en CSV avant l'EDA

##############  FIN PROCEDURE GENERALE ####################################

############## FONCTIONS ####################################

############## Mes fonctions ####################################

############## Mes fonctions ####################################

### ajouter un delay
def random_delay():
    time.sleep(random.uniform(2, 5))


### enlever les baslises html
def remove_html_tags(text_col):
    if text_col is None:
        return None
    else:
        clean = re.compile('<.*?>')
        return re.sub(clean,"", text_col)
    

### convertir l'année de création en année
def convert_year_to_date(value):
    try:
        # Convertir la valeur en int, puis en string et enfin en datetime avec le format %Y
        year_str = str(int(value))
        return pd.to_datetime(year_str, format='%Y').strftime('%Y')
    except:                                                                       # Je retourne la valeur originale si ce n'est pas une date
      return value


### changer le format de la date de publication %Y-%m-%d
def convert_publication_date(value):
    try:
        # Convertir la valeur en int, puis en string et enfin en datetime avec le format %Y
        return pd.to_datetime(value).strftime('%Y-%m-%d')
    except:                                                                       # Je retourne la valeur originale si ce n'est pas une date
      return value


### remplacer les catégories de niveau d'expérience
def experience_replace(experience):
    lower_exp = experience.lower()
    small_exp = lower_exp.replace("_", " ")
    return(small_exp)

### décompacter les tools et les skills
def extract_competences(row):
    skills_col = 'job.skills'                            # je définis les colonnes sur lesquelles je vais passer ma fonction
    tools_col = 'job.tools'                              # directement dans la fonction pour pouvoir la passer sur les 2
    competences = []                                     # j'initialise la liste où je vais enregistrer le tout
    
    # Extraire les outils
    tools_list = row[tools_col]
    if isinstance(tools_list, list):                           # je vérifie que tools_list est une liste
        for dicos in tools_list:                               # je parcours chaque dictionnaire dans la liste des outils
            for key, tool in dicos.items():                    # dans le duo key/value de mes items de chaque dico
                if key == "name":                              # si la clé est = à name
                    competences.append(dicos["name"])          # je stocke l'outil dans la liste
    
    # Extraire les compétences
    skills_list = row[skills_col]
    if isinstance(skills_list, list):                           # je vérifie que skills_list est une liste
        for dictos in skills_list:                              # je parcours chaque dictionnaire dans la liste des compétences
            if 'name' in dictos:                        # je vérifie que la clé 'name' existe dans le dictionnaire
                value = dictos['name']
                if 'fr' in value:                       # je vérifie que la clé 'fr' existe dans le sous-dictionnaire 'name'
                    competences.append(value['fr'])          # je stocke la compétence dans la liste
    
    return competences if competences else None         # je vérifie si des compétences ont été ajoutées à la liste
    
### décompacter les urls des annonces
def jurls_extractor(urls_list):
    if isinstance(urls_list, list):                        # je vérifie que urls_list est une liste
        for dics in urls_list:                             # je parcours chaque dictionnaire dans la liste
            if isinstance(dics, dict) and 'href' in dics:  # je vérifie que dics est un dictionnaire et contient 'href'
                return dics['href']                        # je retourne l'URL
    return None                                            # Retourne None si aucun URL n'a été trouvée

### décompacter les secteurs
def sector_extractor(sectors_list):
    sectors = []                                      # je crée un liste pour stocker mes outils
    if isinstance(sectors_list, list):                   # je vérifie que tools_list est une liste
        for dictos in sectors_list:                       # je parcours chaque dictionnaire dans la liste des outils
            for key, sector in dictos.items():             # dans le duo key/value de mes items de chaque dico
                if key == "name" or key == "parent_name":                       # si la clé est = à name
                    sectors.append(dictos["name", "parent_name"])          # je stocke l'outil dans la liste
            if sectors:  # je vérifie si des outils ont été ajoutées à la liste
                return sectors
        else:
            return None  # je retourne None si aucun outil n'a été trouvé

### Remplacer les noms anglais de CDI/CDD
types_contrats = {'full_time': 'CDI', 'temporary': 'CDD'}

# get est une méthode de dict. elle va chercher la clé passée en argument de la fonction
# si pas égal alors retourne la clé elle-même (d'où le double contrat)
def contract_corrector(contrat):
    return types_contrats.get(contrat, contrat)                 


### Récupérer les départements
def dpt_extractor(zipcode):
    departement = re.search(r"\A\d{2}", zipcode)                # 2 {2}    premiers \A    chiffres \d - le r permet de ne pas prendre \ pour un échappement
    return departement.group(0) if departement else None

############## FIN FONCTIONS ####################################

############## RECUPERATION DES URL DE PAGES ET D'ANNONCES ####################################

## 1. je lance selenium pour aller sur la page de résultats ########################################################################
service = Service(executable_path = 'chromedriver.exe')                         # je dis où est mon driver                       
driver = webdriver.Chrome(service=service)                                      # je définis mon driver
driver.get("https://www.welcometothejungle.com/fr")                                                         # et je l'envoie sur la page d'accueil

wait = WebDriverWait(driver, 8)                                                 # je laisse le temps à la page de se charger

input_element = driver.find_element(By.ID,"search-query-field")                 # je sélectionne la barre de recherche
input_element.clear()                                                           # je la vide au cas où elle est pré-remplie                                             
input_element.send_keys("Data analyst" + Keys.ENTER)                            # j'écris dans la barre de recherche

random_delay()                                                                     # je laisse le temps à la page de charger

## 2. je vais chercher les url de pagination ######################################################################################
page_source = driver.page_source                                   # je vais chercher la page avec mon driver
soup = BeautifulSoup(page_source, "html.parser")                   #  je passe le code HTML à BeautifulSoup pour l'analyser

soup_pages = soup.find('nav', {"aria-label" : "Pagination"})      # Puis je vais chercher la section nav :

if soup_pages is not None:                                        # Je mets un if si la page n'est pas chargée et que nav est vide
    pli = soup_pages.find_all('li')                               # Puis je vais chercher tous les li contenus dans cette nav
    nb_pages = pli[-2].text                                       # Puis je vais chercher le texte de l'avant dernier li 
    print(f"\nJ'ai {nb_pages} pages")                               # (car le dernier c'est la flèche) pour avoir le nombre de pages

else:                                                             # si la page n'a pas eu le temps de charger, j'affiche un message
    print("Aucun élément HTML correspondant au sélecteur spécifié n'a été trouvé.")

result_url = driver.current_url                                   # je récupère l'URL sur laquelle je suis
base_url = result_url.replace("1","")

base_url = "https://www.welcometothejungle.com/fr/jobs?query=data%20analyst&refinementList%5Boffices.country_code%5D%5B%5D=FR&refinementList%5Bcontract_type%5D%5B%5D=full_time&refinementList%5Bcontract_type%5D%5B%5D=temporary&page="
page_number = 1
urls_to_scrape = []

# 3. je fais une boucle qui itère le nom de la page autant de fois que nécessaire
for i in range(1,int(nb_pages)):
    url = f"{base_url}{i}"
    urls_to_scrape.append(url)
print(urls_to_scrape)

random_delay()     

jobs_list = []

for each_page in urls_to_scrape:
    try:
    # je charge la page actuelle dans le navigateur Web
      driver.get(each_page)
      random_delay() 

     # j'attends que la page soit entièrement chargée
      wait = WebDriverWait(driver, 20)
      wait.until(EC.visibility_of_element_located((By.PARTIAL_LINK_TEXT, "Data")))

      links = (driver.find_elements(By.PARTIAL_LINK_TEXT, "Data")        # avec Selenium, je cherche les liens avec data dedans quelque soit la casse 
        or driver.find_elements(By.PARTIAL_LINK_TEXT, "DATA")
        or  driver.find_elements(By.PARTIAL_LINK_TEXT, "data"))

      urls = [link.get_attribute("href") for link in links]              # j'extraits le contenu de href pour le mettre dans la liste urls
      print(urls)
    
      jobs_list.extend(urls)
    except:
        print(f"An error occured on page {driver.current_url}")  

print(f"J'ai {len(jobs_list)} annonces au total")
print(jobs_list)

driver.quit()                                                     # je ferme le navigateur une fois tout fini

############## FIN RECUPERATION DES URL DE PAGES ET D'ANNONCES ####################################

############## RECUPERATION DES DONNES DE TOUTES LES ANNONCES ####################################

## 1. formatage des urls en relative pour le requêtage ##

relative_urls = [sub.replace("https://www.welcometothejungle.com/fr/companies", "") for sub in jobs_list]
print(relative_urls)
print(len(relative_urls))                               # je vérifie que je n'ai rien perdu

## 2. formatage des urls relatives en url de requêtage ##
api_urls = []
for url in relative_urls:
    api_url = f"https://api.welcometothejungle.com/api/v1/organizations{url}"
    api_urls.append(api_url)
print(api_urls)
print(len(api_urls))                       # je vérifie que je n'ai rien perdu

## 3.  je requête chaque URL et je stocke dans un dataframe ########

# création d'une liste vide pour stocker les données JSON
data_json = []

for job_url in api_urls:
    link = job_url
    r = requests.get(link)
    data_json.append(json.loads(r.text))                # comme j'itère sur chaque url je dois stocker ce résultat dans une liste
    # print(json.dumps(data_json, indent=2))

# j'en fais un dataframe
df_jraw = pd.json_normalize(data_json)
df_jraw

## 4. je nettoie et je formate ## 

## 4. je nettoie et je formate ## 

# 4.1 je drop toutes les colonnes dont je n'ai pas besoin
df_jobs_temp = df_jraw.drop(columns=["job.slug", 
                                   "job.videos", 
                                   "job.updated_at",
                                   "job.offices",
                                   "job.apply_url", 
                                   "job.is_default",
                                   'job.organization.has_external_ats',
                                   'job.organization.labels',
                                   'job.organization.logo.url', 
                                   'job.organization.logo.thumb.url',
                                   'job.organization.sectors',
                                   'job.organization.cover_image.small.url',
                                   'job.organization.cover_image.url',
                                   'job.organization.cover_image.medium.url',
                                   'job.organization.cover_image.large.url',
                                   'job.organization.cover_image.social.url',
                                   'job.organization.website_organization.slug',
                                   'job.organization.website_organization.i18n_descriptions.fr',
                                   'job.organization.gdpr_setting.application_message',
                                   'job.organization.gdpr_setting.consent_duration',
                                   'job.organization.gdpr_setting.privacy_policy_url',
                                   'job.organization.media_website_url',
                                   'job.organization.headquarter.address',
                                   'job.organization.headquarter.local_address',
                                   'job.organization.headquarter.city',
                                   'job.organization.headquarter.latitude',
                                   'job.organization.headquarter.longitude',
                                   'job.organization.headquarter.district',
                                   'job.organization.headquarter.country_code',
                                   'job.organization.headquarter.zip_code',
                                   'job.organization.headquarter.local_city',
                                   'job.organization.headquarter.local_district',
                                   'job.organization.media_facebook',
                                   'job.organization.media_instagram',
                                   'job.organization.media_linkedin',
                                   'job.organization.media_pinterest',
                                   'job.organization.media_twitter',
                                   'job.organization.media_youtube',
                                   'job.organization.playlist_id',
                                   'job.organization.video_playlist_provider',
                                   'job.organization.automatic_email',
                                   'job.archived_at',
                                   'job.profession.name.cs', 'job.profession.name.en',
                                   'job.profession.name.es', 'job.profession.name.sk',
                                   'job.profession.category.cs',
                                   'job.profession.category.en', 'job.profession.category.es',
                                   'job.profession.category.fr', 'job.profession.category.sk',
                                   'job.profession.category_name.cs',
                                   'job.profession.category_name.en',
                                   'job.profession.category_name.es',
                                   'job.profession.category_name.sk',
                                   'job.profession.sub_category_name.cs',
                                   'job.profession.sub_category_name.en',
                                   'job.profession.sub_category_name.es',
                                   'job.profession.sub_category_name.sk',
                                   'job.profession.sub_category_reference',
                                   'job.questions',
                                   "job.featured_page.type",
                                   'job.featured_page.slug',
                                   'job.cta_content.links',
                                   'job.cta_content.contents',
                                   'job.organization.website_organization.i18n_descriptions.en',
                                   'job.organization.website_organization.i18n_descriptions.es',
                                   'job.status',
                                   'job.profession.name.fr',
                                   'job.organization.reference',
                                   'job.organization.default_language',
                                   'job.organization.parity_men',
                                   'job.organization.revenue',
                                   'job.organization.average_age',
                                   'job.salary_currency',
                                   'job.salary_period',
                                   'job.profession.category_reference',
                                   'job.office.address',
                                   'job.office.local_address',
                                   'job.office.district',
                                   'job.office.country_code',
                                   'job.office.local_city',
                                   'job.office.local_district',
                                   'job.language',
                                   'job.start_date',
                                   'job.recruitment_process',
                                   'job.featured_page',
                                   'job.organization.gdpr_setting',
                                   'job.organization.gdpr_setting',
                                   'job.organization.equality_indexes',
                                   'job.organization.equality_indexes.equality_among_highest_earners',
                                   'job.organization.equality_indexes.gap_in_annual_raises',
                                   'job.organization.equality_indexes.gap_in_annual_raises_excluding_promotions',
                                   'job.organization.equality_indexes.gap_in_promotions',
                                   'job.organization.equality_indexes.gender_pay_gap',
                                   'job.organization.equality_indexes.maternity_leave_return_raise',
                                   'job.organization.equality_indexes.published',
                                   'job.organization.equality_indexes.workforce_range',
                                   'job.organization.equality_indexes.year',
                                   'job.organization.turnover',
                                   'job.organization.jobs_count',
                                   'job.organization.website_organization.i18n_descriptions.en',
                                   'job.benefits.FR.categories',
                                   'job.benefits.FR.count',
                                   'job.benefits.FR.preview',
                                   'job.organization.website_organization.i18n_descriptions.es',
                                   'job.apply_url',
                                   "job.organization.profile_type",
                                    'job.contract_duration_max',
                                    'job.contract_duration_min',
                                    'job.profession.category_name.fr',
                                    'job.profession.sub_category_name.fr',
                                    'job.wttj_reference',
                                    'job.company_description',
                                   ]
                                   )

# 4.2 je passe toutes mes fonctions

# html cleaner
### faire un if none pass sinon
df_jobs_temp[["job.organization.description_clean","job.profile_clean", "job.description_clean"]] = df_jobs_temp[["job.organization.description","job.profile", "job.description"]].map(remove_html_tags).copy()

# level bins cleaner
df_jobs_temp["job.experience_level_clean"] = df_jobs_temp["job.experience_level"].astype(str).apply(lambda x: experience_replace(x))
df_jobs_temp["job.education_level_clean"] = df_jobs_temp["job.education_level"].astype(str).apply(lambda x: experience_replace(x))

# date convertor
df_jobs_temp['job.organization.creation_year_date'] = df_jobs_temp['job.organization.creation_year'].apply(convert_year_to_date)

df_jobs_temp['competences'] = df_jobs_temp.apply(extract_competences, axis=1)

# job urls extractor
df_jobs_temp["job.urls_clean"] = df_jobs_temp["job.urls"].apply(jurls_extractor)

# type de contrats
df_jobs_temp['job.contract_type'] = df_jobs_temp['job.contract_type'].apply(contract_corrector)

# départements
df_jobs_temp["departement"] = df_jobs_temp['job.office.zip_code'].astype(str).apply(dpt_extractor)

# date de publication
df_jobs_temp['date_publication'] = df_jobs_temp['job.published_at'].apply(convert_publication_date)

# 4.3 j'ajoute quelques colonnes nécessaires

# je calcule le salaire moyen
df_jobs_temp['salaire_avg'] = ((df_jobs_temp['job.salary_max'] + df_jobs_temp['job.salary_min']) / 2)

# Je concatane dans description_job mes colonne job description et job profile
df_jobs_temp["description_job"] = df_jobs_temp["job.description_clean"].astype(str) + " --- " + df_jobs_temp["job.profile_clean"]

# 4.4 puis je drop les colonnes que j'ai nettoyées
df_jobs = df_jobs_temp.drop(columns=["job.skills", "job.tools", "job.application_fields", "job.profile", "job.organization.description", 
                                     "job.organization.creation_year", "job.urls",'job.profile_clean', 'job.description_clean', 
                                   'job.description',"job.organization.description",'job.published_at','job.experience_level','job.education_level', 'job.office.zip_code',])


# 4.5 je renomme mes colonnes 

df_jobs2 = df_jobs.rename(columns={"job.contract_type": "contrat", 
                                   "job.remote": "teletravail", 
                                   "job.organization.nb_employees": "nb_employes", 
                                   "job.organization.equality_indexes.equality_index": "index_egalite",
                                   'job.organization.industry': "secteur", 
                                   'job.organization.parity_women': "repartition_genre",
                                   'job.organization.name': "nom_entreprise",
                                   'job.reference': "reference",
                                   'job.salary_min': "salaire_min", 
                                   'job.name': "nom_emploi", 
                                   'job.organization.description_clean': "description_cie",
                                   'job.salary_max': "salaire_max", 
                                   'job.office.city': "ville", 
                                   'job.office.latitude': "office_latitude",
                                   'job.office.longitude': "office_longitude", 
                                   'job.experience_level_clean': "niveau_experience",
                                   'job.education_level_clean': "niveau_etudes", 
                                   'job.organization.creation_year_date': "company_creation",
                                   'job.urls_clean': "url",
                                   })

# 4.6 j'ajoute la colonne impact
df_jobs2["impact"] = np.nan

# 4.7 je réordonne mes colonnes
df_wtjj = df_jobs2[['nom_entreprise',
                   'nom_emploi',
                    'description_cie',
                    'description_job',
                    'salaire_min',
                    'salaire_max',
                    'salaire_avg',
                    'ville',
                    'departement',
                    'contrat',
                    'niveau_experience',
                    'niveau_etudes',
                    'teletravail',
                    'competences',
                    'date_publication',
                    'secteur',
                    'nb_employes',
                    'url',
                    'impact',
                    'index_egalite',
                    'repartition_genre',
                    'company_creation',
                    'reference',
                    'office_latitude',
                    'office_longitude']]

# 5. j'exporte en csv avec date et heure du moment

# today = date.today()
now = datetime.now()

# Étape 2: je formate la date dd-mm-hh-mn
formatted_date = now.strftime("%d-%m_%H-%M")

# 5.1. j'exporte le df complet pour la viz

# Étape 3: j'ajoute la date au nom de fichier
full_file = f"fullwttj_{formatted_date}.csv"

df_wtjj.to_csv(full_file, index=False)

# 5.2 j'exporte le df strict pour le site
# pour cela je drop qq colonnes

df_strict_wtjj = df_wtjj.drop(columns=['nom_entreprise',
                   'nom_emploi',
                    'description_cie',
                    'description_job',
                    'salaire_min',
                    'salaire_max',
                    'salaire_avg',
                    'ville',
                    'departement',
                    'contrat',
                    'niveau_experience',
                    'niveau_etudes',
                    'teletravail',
                    'competences',
                    'date_publication',
                    'secteur',
                    'nb_employes',
                    'url',
                    'impact',
                    'index_egalite',
                    'repartition_genre'])

# Étape 3: j'ajoute la date au nom de fichier
strict_file = f"wttj_{formatted_date}.csv"

df_wtjj.to_csv(strict_file, index=False)

############## FIN RECUPERATION DES DONNES DE TOUTES LES ANNONCES ####################################