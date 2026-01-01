from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from researcher import search_arxiv, extract_text_from_pdf
from analyzer import analyze_research_with_gemini
import uvicorn
import os

app = FastAPI()

# HTML dosyasının okunabilmesi için
if not os.path.exists("static"):
    os.makedirs("static")

@app.get("/", response_class=HTMLResponse)
async def get_ui():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/research")
async def start_research(query: str):
    papers = search_arxiv(query)
    
    for paper in papers:
        if paper.get('pdf_url'):
            paper['full_text'] = extract_text_from_pdf(paper['pdf_url'])
    
    analysis_result = analyze_research_with_gemini(query, papers)
    
    return {
        "topic": query,
        "analysis": analysis_result,
        "sources": papers
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)