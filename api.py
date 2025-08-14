# api.py
from fastapi import FastAPI, Query
from scraping import scrape_fintrac_notices, scrape_OSFI_notices, scrape_OSC_notices, scrape_all_articles

app = FastAPI(
    title="Cidel RIO",
    version="1.0.0",
    servers=[
        {"url": "https://RIO.cidel.onrender.com", "description": "Production"}
    ]
)

@app.get("/")
def root():
    return {"message": "It’s working!"}

@app.get("/articles")
def get_articles():
    return scrape_all_articles()
