import os
import requests
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from textblob import TextBlob
from typing import List, Optional
from fastapi.middleware.cors import CORSMiddleware

# Configuração do FastAPI
app = FastAPI(
    title="API de análise de sentimentos de noticias",
    description="Uma API que busca notícias sobre um termo e analisa o sentimento de seus títulos.",
    version="1.0.0"
)

# Habilitar Cors
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Variáveis de ambiente para a API de notícias
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "SUA_CHAVE_AQUI")
print("NEWS_API_KEY:", NEWS_API_KEY)
NEWS_API_URL = "https://newsapi.org/v2/everything"

# Estrutura do modelo de resposta
class AnalyzedArticle(BaseModel):
    title: str = Field(..., description="Título da notícia")
    author: Optional[str] = Field(None, description="Autor da notícia")
    source_name: str = Field(..., description="Nome da fonte da notícia")
    url: str = Field(..., description="URL da notícia")
    sentiment: str = Field(..., description="Sentimento do título da notícia (positivo, negativo, neutro)")
    polarity: float = Field(..., description="Score de polaridade do título da notícia")

# Modelo de resposta completo
class NewsSentimentResponse(BaseModel):
    search_term: str = Field(..., description="Termo pesquisado")
    articles_found: int = Field(..., description="Número de notícias encontradas")
    articles: List[AnalyzedArticle] = Field(..., description="Lista de notícias analisadas")    

def get_sentiment(text: str) -> tuple[str, float]:
    """Analisa o sentimento do texto usando TextBlob."""
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0.1:
        return "Positivo", polarity
    elif polarity < -0.1:
        return "Negativo", polarity
    else:
        return "Neutro", polarity

@app.get("/analyze", response_model=NewsSentimentResponse)
def analyze_news_sentiment(
    q: str = Query(..., description="O termo de busca para as notícias (ex: 'Tesla', 'Brasil').", min_length=2)
):
    """
    Busca notícias sobre um termo, analisa o sentimento dos títulos e retorna os resultados.
    """
    if not NEWS_API_KEY:
        raise HTTPException(
            status_code=500,
            detail="A chave da NewsAPI não foi configurada nas variáveis de ambiente."
        )
    params = {
        "q": q,
        "apiKey": NEWS_API_KEY,
        "language": "pt",
        "pageSize": 20,
        "sortBy": "publishedAt"
    }

    try:
        response = requests.get(NEWS_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=503, detail=f"Erro ao conectar com a NewsAPI: {e}")
    
    analyzed_articles = []
    for article in data.get("articles", []):
        if not article.get("title"):
            continue
        sentiment, polarity = get_sentiment(article["title"])
        analyzed_articles.append(
            AnalyzedArticle(
                title=article["title"],
                author=article.get("author"),
                source_name=article["source"]["name"],
                url=article["url"],
                sentiment=sentiment,
                polarity=polarity
            )
        )

    return NewsSentimentResponse(
        search_term=q,
        articles_found=len(analyzed_articles),
        articles=analyzed_articles
    )

@app.get("/")
def read_root():
    return {"message": "Bem-vindo à API de Análise de Sentimento de Notícias! Acesse /docs para a documentação interativa."}