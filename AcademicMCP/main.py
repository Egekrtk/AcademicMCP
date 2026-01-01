from fastapi import FastAPI
from researcher import search_arxiv, extract_text_from_pdf
from analyzer import analyze_research_with_gemini # İsim düzeltildi
import uvicorn

app = FastAPI()

@app.get("/research")
async def start_research(query: str):
    # 1. Makaleleri bul
    papers = search_arxiv(query)
    
    # 2. PDF içeriğini çek (researcher.py'daki yapıya göre güncellendi)
    for paper in papers:
        if paper.get('pdf_url'):
            print(f"İçerik çekiliyor: {paper['title']}")
            # researcher.py'daki fonksiyonu çağırıyoruz
            paper['full_text'] = extract_text_from_pdf(paper['pdf_url'])
    
    # 3. Gemini ile analiz et
    analysis_result = analyze_research_with_gemini(query, papers)
    
    return {
        "topic": query,
        "analysis": analysis_result,
        "sources": papers
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)