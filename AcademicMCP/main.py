
from fastapi import FastAPI
from researcher import search_academic_papers, extract_text_from_pdf
from analyzer import analyze_research
import uvicorn

app = FastAPI()

@app.get("/research")
async def start_research(query: str):
    # 1. Makaleleri bul
    papers = search_academic_papers(query)
    
    # 2. Ücretsiz olanların tam metnini çek
    for paper in papers:
        if paper.get('isOpenAccess') and paper.get('openAccessPdf'):
            pdf_url = paper['openAccessPdf']['url']
            paper['full_text'] = extract_text_from_pdf(pdf_url)
    
    # 3. Gemini ile analiz et
    analysis_result = analyze_research(query, papers)
    
    return {
        "topic": query,
        "analysis": analysis_result,
        "sources": papers
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)