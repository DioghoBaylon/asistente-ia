from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import joblib
import re

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://asistenteupao.netlify.app"],  # ⚠️ Dominio exacto de tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rutas estáticas y plantillas
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Cargar modelo y datos
model = joblib.load("svm_model.pkl")
vectorizer = joblib.load("tfidf_vectorizer.pkl")
le = joblib.load("label_encoder.pkl")
df = pd.read_csv("df_total.csv")

def limpiar_texto(texto):
    texto = str(texto).lower()
    texto = re.sub(r'[^\w\s]', '', texto)
    texto = re.sub(r'\d+', '', texto)
    return texto

def buscar_mejor_respuesta(pregunta, categoria, dataframe, vectorizador):
    preguntas_categoria = dataframe[dataframe["Categoría"] == categoria].copy()
    preguntas_categoria["Pregunta_procesada"] = preguntas_categoria["Pregunta"].apply(limpiar_texto)
    tfidf_matrix = vectorizer.transform(preguntas_categoria["Pregunta_procesada"])
    pregunta_vec = vectorizer.transform([limpiar_texto(pregunta)])
    similitudes = cosine_similarity(pregunta_vec, tfidf_matrix).flatten()
    idx_mejor = similitudes.argmax()
    mejor_respuesta = preguntas_categoria.iloc[idx_mejor]["Respuesta"]
    return mejor_respuesta

class Pregunta(BaseModel):
    texto: str

@app.get("/", response_class=HTMLResponse)
def serve_home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/preguntar")
def responder(pregunta: Pregunta):
    pregunta_limpia = limpiar_texto(pregunta.texto)
    pregunta_vect = vectorizer.transform([pregunta_limpia])
    pred_cod = model.predict(pregunta_vect)[0]
    categoria = le.inverse_transform([pred_cod])[0]
    respuesta = buscar_mejor_respuesta(pregunta.texto, categoria, df, vectorizer)
    return {"categoria": categoria, "respuesta": respuesta}
