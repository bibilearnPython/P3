from dotenv import load_dotenv
import os
import pandas as pd

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.schema import Document
from langchain_community.vectorstores import FAISS

from langchain_core.runnables import RunnablePassthrough
from langchain.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_groq import ChatGroq


# charger le csv
df = pd.read_csv("jobs_all.csv", sep=",")

#récupérer les colonnes utile du df et les récupérer sous format d'une liste de document
documents = []
for i, r in df.iterrows():
    meta = {col : r[col] for col in ['nom_emploi',
                                     'nom_entreprise',
                                     'description_cie',
                                     'description_job',
                                     'ville',
                                     'contrat',
                                     'niveau_experience',
                                     'teletravail']}
    page = "\n".join(str(r[col]) for col in ['nom_emploi',
                                            'nom_entreprise',
                                            'description_cie',
                                            'description_job',
                                            'ville',
                                            'contrat',
                                            'niveau_experience',
                                            'teletravail'])
    doc = Document(
        page_content=page,
        metadata=meta,
    )
    documents.append(doc)


# split documents to chunk
text_splitter = RecursiveCharacterTextSplitter(separators=['\n','\n\n','\r'],

    chunk_size=2000,
    chunk_overlap=200,
    length_function=len,
    is_separator_regex=False,
)

docs = text_splitter.split_documents(documents)

# define embedding
embeddings_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")

def faiss_store(embedding , doc ):
    # Créer le VectorStore FAISS et ajouter les documents
    return FAISS.from_documents(doc, embedding)

# je vectorise et je mets dans ma db
db = faiss_store(doc = docs, embedding=embeddings_model)


# définir model llm
load_dotenv()
key = os.getenv('KEY')
def chat_groq(t = 0, choix = "llama3-70b-8192", api = key) :
    return ChatGroq(temperature = t, model_name = choix, groq_api_key = api)

model_chat = chat_groq()



message = """
Tu es un assistant de recherche emploi pour l'entreprise CandiData,
du dois tenir compte de mes besoin pour recommander les annonces d'emplois les plus appropriées à mon profil.
N'hésite pas à faire des blagues sur des mots candy (sucre, douceur, ...), data et candidate.
À ma demande tu me retourneras 3 emplois les plus proches dans ma base de données.
Utilise ce contexte pour répondre. Si tu n'as pas de réponse, dis-le.
Redonne tous les détails de chaque job.
{question}

Context:
{context}
"""
retriever = db.as_retriever()

prompt = ChatPromptTemplate.from_messages([("human", message)])

rag_chain = {"context": retriever, "question": RunnablePassthrough()} | prompt | model_chat


# fonction pour faire une demande
def match_jobs(chat_texte):
    r = rag_chain.invoke(chat_texte)
    return r.content