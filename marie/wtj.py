from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random

import pandas as pd
import requests
from bs4 import BeautifulSoup
import json
import re


##############  PROCEDURE GENERALE ####################################
# 1. Aller sur la page de résultats avec selenium
# 2. Récupérer les URL pour aller de page en page
# 3. Faire une fonction pour aller récupérer les URL de chaque annonce sur chaque page
# 4. Couper les URL en relatif puis les reconcatener pour les passer dans l'API
# 5. Itérer pour requêter l'API avec chaque URL récupérée sur chaque page de résultats
# 6. Transformer en dataframe, décompacter et dropper ce qui doit l'être
# 7. Exporter en CSV avant l'EDA

##############  FIN PROCEDURE GENERALE ####################################

############## FONCTIONS ####################################

### Delay
def random_delay():
    time.sleep(random.uniform(2, 5))

### enlever les baslises html
def remove_html_tags(text_col):
    if text_col is None:
        return None
    else:
        clean = re.compile('<.*?>')
        return re.sub(clean,"", text_col)

### décompacter les tools
def jtools_extractor(col):
    tools = []                                      # je crée un liste pour stocker mes outils
    for dicos in (df_job_temp["job.tools"][0]):     # je vais chercher chaque dico contenu dans le premier (et seul) item de ma liste de cette colonne
        for key, tool in dicos.items():             # dans le duo key/value de mes items de chaque dico
            if key == "name":                       # si la clé est = à name
                tools.append(dicos["name"])         # alors je stocke cet outil dans une liste
    # return ", ".join(tools)                       # attention à bien remonter return en dehors de la deuxième boucle for
    return(tools)

### décompacter les skills
def jskills_extractor(col):
    skills = []                                         # je crée un liste pour stocker mes skills
    for dictos in (df_job_temp["job.skills"][0]):       # je vais chercher chaque dico contenu dans le premier item de ma liste de cette colonne
        for key, value in dictos.items():               # dans le duo key/value de mes items de chaque dico
            if key == "name":                           # je vais chercher l'item name
               for sec_key, skill in value.items():     # cet item étant un dict. je cherche la paire k/v
                   if sec_key == "fr":                  # si la clé est = à name
                         skills.append(skill)           # alors je stocke cette skill dans une liste
    return(skills)

### récupérer ce qui est obligatoire pour la candidature
def appli_mandatory_extractor(col):
    applications = []                                           # je crée un liste pour stocker mes éléments mandatory
    for dicts in (df_job_temp["job.application_fields"][0]):    # je vais chercher chaque dico contenu dans le premier (et seul) item de ma liste de cette colonne
            for key, value in dicts.items():                    # dans le duo key/value de mes items de chaque dico
                if value == "mandatory":                        # si une value est = à mandatory
                    applications.append(dicts["name"])          # alors je stocke chaque clé correspondante à name
    return(applications)

############## FIN FONCTIONS ####################################

############## RECUPERATION DES URL DE PAGES ET D'ANNONCES ####################################

## 1. je lance selenium pour aller sur la page de résultats ########
service = Service(executable_path = 'chromedriver.exe')                         # je dis où est mon driver                       
driver = webdriver.Chrome(service=service)                                      # je définis mon driver
driver.get("https://www.welcometothejungle.com/fr")                                                         # et je l'envoie sur la page d'accueil

wait = WebDriverWait(driver, 8)                                                 # je laisse le temps à la page de se charger

input_element = driver.find_element(By.ID,"search-query-field")                 # je sélectionne la barre de recherche
input_element.clear()                                                           # je la vide au cas où elle est pré-remplie                                             
input_element.send_keys("Data analyst" + Keys.ENTER)                            # j'écris dans la barre de recherche

random_delay()                                                                  # je laisse le temps à la page de charger

## 2. je vais chercher les url de pagination ########
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

## 3. je fais une boucle qui itère le nom de la page autant de fois que nécessaire ########
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

## 1. formatage des urls en relative pour le requêtage ########

relative_urls = [sub.replace("https://www.welcometothejungle.com/fr/companies", "") for sub in jobs_list]
print(relative_urls)
print(len(relative_urls))                               # je vérifie que je n'ai rien perdu

## 2. formatage des urls relatives en url de requêtage ########
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

## 4. je nettoie et je formate ## 

# 4.1 je drop toutes les colonnes dont je n'ai pas besoin
df_jobs_temp = df_jraw.drop(columns=["job.urls", 
                                   "job.slug", 
                                   "job.videos", 
                                   "job.updated_at",
                                   "job.offices", 
                                   "job.is_default",
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
                                   ]
                                   )

# 4.2 je passe toutes mes fonctions

# html cleaner
### faire un if none pass sinon
df_jobs_temp[["job.organization.description_clean","job.profile_clean"]] = df_jobs_temp[["job.organization.description","job.profile"]].map(remove_html_tags).copy()

# tools extractor
df_jobs_temp["job.tools_clean"] = df_jobs_temp["job.tools"].apply(jtools_extractor)

# skills extractor
df_jobs_temp["job.skills_clean"] = df_jobs_temp["job.skills"].apply(jskills_extractor)

# application mandatories
df_jobs_temp["job.application_mandatory"] = df_jobs_temp["job.application_fields"].apply(appli_mandatory_extractor)

# 4.3 puis je drop les colonnes que j'ai nettoyé
df_jobs = df_jobs_temp.drop(columns=["job.skills", "job.tools", "job.application_fields", "job.profile","job.organization.description_clean"])

df_jobs.sample(5)

df_jobs.to_csv('wttj-1106.csv', index=False)  

############## FIN RECUPERATION DES DONNES DE TOUTES LES ANNONCES ####################################