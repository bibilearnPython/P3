"""
merge de toutes les compétences (création chat, saisie manuelle, offres welcome to the jungle)
création de deux listes:
1) comp_vecto (tokens)
2) comp_str (strings - compétences qui sont plus long qu'un mot)
"""

from comp_1 import competences_single, competences_multi
from comp_2 import competences_welcome

import pickle

comp_vecto = []
comp_str = []

for comp in competences_welcome:
    if " " in comp:
        comp_str.append(comp)
    else:
        comp_vecto.append(comp)

for comp in competences_single:
    if comp not in comp_vecto:
        comp_vecto.append(comp)

for comp in competences_multi:
    if comp not in comp_str:
        comp_str.append(comp)

# print(f"Single tokens: {comp_vecto}")
# print()
# print(f"Strings: {comp_str}")


# Save the lists to a file using pickle
# opens a file in write-binary mode
with open("comp_vecto.pkl", "wb") as file:
    pickle.dump(comp_vecto, file)

with open("comp_str.pkl", "wb") as file:
    pickle.dump(comp_str, file)