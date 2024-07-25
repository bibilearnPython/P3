import pandas as pd

df = pd.read_csv("candidata_v2.csv", sep=",")

def group(nom):
    new = nom
    nom = str(nom).lower()

    if "data analyst" in nom:
        new = "Data Analyst"
    elif "data engineer" in nom:
        new = "Data Engineer"
    elif "data scientist" in nom:
        new = "Data Scientist"
    
    if "senior" in nom:
        new = "Senior" + " " + new
    elif "junior" in nom or "débutant" in nom:
        new = "Junior" + " " + new
    elif "confirmé" in nom:
        new = new + " " + "confirmé"
    
    return new

df["nom_emploi_group"] = df["nom_emploi"].apply(group)

df = df[["nom_emploi_group"]]

df.to_csv("candidata_emploi.csv", sep=",", encoding="utf-8", index=False)