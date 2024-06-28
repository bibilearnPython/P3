""" fonction pour extraire les compétences d'une description du poste """
import nltk
nltk.download("popular")
import pickle

# open lists
# open the pickle files in read-binary mode
# deserialize the contents back into a list
with open("comp_vecto.pkl", "rb") as file:
    comp_vecto = pickle.load(file)

with open("comp_str.pkl", "rb") as file:
    comp_str = pickle.load(file)

# function
def competences(description):

    description_tokens = nltk.word_tokenize(description.lower())
    competences_list = []

    for i in comp_vecto:
        if i in description_tokens and i not in competences_list:
            competences_list.append(i)

    for i in comp_str:
        if i in description and i not in competences_list:
            competences_list.append(i)

    if competences_list == []:
        competences_list = None

    return competences_list   