import requests



# def requete(nom):
#     url = f"https://base-donnees-publique.medicaments.gouv.fr/?query={nom}"
#     response = requests.get(url)
#     if response.status_code == 200:
#         medicaments = response.json()
#         return medicaments
#     else:
#         print("Erreur lors de la requête :", response.status_code)
        
# print(requete("doliprane"))





# import requests
# from bs4 import BeautifulSoup

# def rechercher_medicament(nom_medicament):
#     base_url = "https://base-donnees-publique.medicaments.gouv.fr"
#     recherche_url = f"{base_url}/index.php"
    
#     params = {
#         'page': 1,
#         'txtCaracteres': nom_medicament,
#         'btnMedic.x': 0,
#         'btnMedic.y': 0,
#         'btnMedic': 'Rechercher',
#     }
    
#     headers = {
#         'User-Agent': 'Mozilla/5.0'
#     }

#     response = requests.get(recherche_url, params=params, headers=headers)
#     soup = BeautifulSoup(response.text, 'html.parser')

#     # Recherche tous les liens vers les fiches médicament
#     liens = soup.select("a.lienMedic")
    
#     print(f"Résultats pour '{nom_medicament}':")
#     for lien in liens[:5]:  # Limité aux 5 premiers
#         texte = lien.get_text(strip=True)
#         url = base_url + '/' + lien['href']
#         print(f"- {texte} : {url}")

# rechercher_medicament("doliprane")








from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Attendre que les liens apparaissent (10 secondes max)






def rechercher_medicament_selenium(nom_medicament):
    # Lancement du navigateur (ici avec Chrome)
    driver = webdriver.Chrome(service=Service("/usr/local/bin/chromedriver-137"))
    driver.get("https://base-donnees-publique.medicaments.gouv.fr")

    # Entrée du nom du médicament
    champ_recherche = driver.find_element(By.NAME, "txtCaracteres")
    champ_recherche.send_keys(nom_medicament)
    champ_recherche.send_keys(Keys.RETURN)

    # Attente du chargement de la page
    # time.sleep(3)
    
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "listeResultats")))

    # Récupération des liens vers les fiches médicament
    liens = driver.find_elements(By.CSS_SELECTOR, "a.lienMedic")
    
    print(liens)
    print(f"Résultats pour '{nom_medicament}' :")
    for lien in liens[:5]:  # On limite à 5 résultats
        print(f"- {lien.text} : {lien.get_attribute('href')}")

    driver.quit()

# rechercher_medicament_selenium("doliprane")





from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def rechercher_medicament_selenium(nom_medicament):
    selecteur = 'a[href*="extrait.php?specid="]'
    driver = webdriver.Chrome(service=Service("/usr/local/bin/chromedriver-137"))
    driver.get("https://base-donnees-publique.medicaments.gouv.fr")

    # Remplir le champ de recherche
    champ_recherche = driver.find_element(By.NAME, "txtCaracteres")
    champ_recherche.send_keys(nom_medicament)
    champ_recherche.send_keys(Keys.RETURN)

    try:
        # Attendre que les liens apparaissent (5s max)
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selecteur))
        )

        # Récupérer les liens vers les fiches médicaments
        liens = driver.find_elements(By.CSS_SELECTOR, selecteur)
        for lien in liens[:5]:
            print(f"{lien.text.strip()} : https://base-donnees-publique.medicaments.gouv.fr/{lien.get_attribute('href')}")

    except Exception as e:
        print("❌ Aucun lien trouvé.")
        print(e)

    finally:
        driver.quit()

# rechercher_medicament_selenium("doliprane")






from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def get_description_premier_medicament(nom_medicament):
    selecteur_lien = 'a[href*="extrait.php?specid="]'
    selecteur_text = 'p.AmmCorpsTexte'
    driver = webdriver.Chrome(service=Service("/usr/local/bin/chromedriver-137"))
    driver.get("https://base-donnees-publique.medicaments.gouv.fr")

    # Recherche du médicament
    champ_recherche = driver.find_element(By.NAME, "txtCaracteres")
    champ_recherche.send_keys(nom_medicament)
    champ_recherche.send_keys("\n")

    try:
        # Attente des liens
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, selecteur_lien))
        )

        # Récupération du 1er lien
        lien = driver.find_elements(By.CSS_SELECTOR, selecteur_lien)[0]
        url = lien.get_attribute("href")
        print("🔗 Accès à :", url)

        # Aller sur la page du médicament
        driver.get(url)

        
        # Attendre que les paragraphes soient présents
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, selecteur_text))
        )

        paragraphes = driver.find_elements(By.CSS_SELECTOR, selecteur_text)
        print(f"Nombre de paragraphes trouvés : {len(paragraphes)}\n")

        for i, p in enumerate(paragraphes, start=1):
            print(f"Paragraphe {i} :")
            print(p.text)
            print("-" * 40)

    except Exception as e:
        print("❌ Erreur :", e)

    finally:
        driver.quit()


get_description_premier_medicament("doliprane")

