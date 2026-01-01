from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from researcher import search_arxiv, extract_text_from_pdf
from analyzer import analyze_research_with_gemini
import uvicorn
import os

app = FastAPI()

# Ana dizini belirle
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "Hata: static/index.html dosyası bulunamadı!"

@app.get("/research")
async def start_research(query: str):
    # 1. Makaleleri bul
    papers = search_arxiv(query)
    
    # 2. PDF'lerin tamamını işle
    for paper in papers:
        if paper.get('pdf_url'):
            paper['full_text'] = extract_text_from_pdf(paper['pdf_url'])
    
    # 3. Gemini ile detaylı analiz yap
    analysis_result = analyze_research_with_gemini(query, papers)
    
    return {
        "topic": query,
        "analysis": analysis_result,
        "sources": papers
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)