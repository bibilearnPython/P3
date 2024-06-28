# Competences

Le fichier **competences.py** contient une fonction **competences** qui prend un string pour argument et renvoie une liste de competences.


from competences import competences

dataframe["competences"] = dataframe["description_job"].apply(competences)


Il faut lancer le script dans le même dossier ou se trouve **competences.py** et les fichiers au format pickle **comp_str.pkl** et **comp_vecto.pkl**

Le dossier **process** contient des fichiers python avec des comentaires avec lesquels j'ai crée les fichiers pickles. Il y en a également des notes sur les prompts pour chatgpt pour une première liste de compétences.