from fastapi import FastAPI
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import LinearSVC
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import joblib
import re

app = FastAPI()

model = joblib.load("svm_model.pkl")
vectorizer = joblib.load("tfidf_vectorizer.pkl")
le = joblib.load("label_encoder.pkl")
df = pd.read_csv("df_total.csv")

def limpiar_texto(texto):
    texto = str(texto).lower()
    texto = re.sub(r"[^\w\s]", "", texto)
    texto = re.sub(r"\d+", "", texto)
    return texto

def buscar_mejor_respuesta(pregunta, categoria, dataframe, vectorizador):
    preguntas_categoria = dataframe[dataframe["Categoría"] == categoria].copy()
    preguntas_categoria["Pregunta_procesada"] = preguntas_categoria["Pregunta"].apply(limpiar_texto)
    tfidf_matrix = vectorizador.transform(preguntas_categoria["Pregunta_procesada"])
    pregunta_vec = vectorizador.transform([limpiar_texto(pregunta)])
    similitudes = cosine_similarity(pregunta_vec, tfidf_matrix).flatten()
    idx_mejor = similitudes.argmax()
    mejor_respuesta = preguntas_categoria.iloc[idx_mejor]["Respuesta"]
    return mejor_respuesta

class Pregunta(BaseModel):
    texto: str

@app.post("/preguntar")
def responder(pregunta: Pregunta):
    pregunta_limpia = limpiar_texto(pregunta.texto)
    pregunta_vect = vectorizer.transform([pregunta_limpia])
    pred_cod = model.predict(pregunta_vect)[0]
    categoria = le.inverse_transform([pred_cod])[0]
    respuesta = buscar_mejor_respuesta(pregunta.texto, categoria, df, vectorizer)
    return {"categoria": categoria, "respuesta": respuesta}
