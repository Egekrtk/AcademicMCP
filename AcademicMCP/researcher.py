import requests
import xml.etree.ElementTree as ET
import fitz  # PyMuPDF
import io
import time

def search_arxiv(query, max_results=3):
    base_url = "http://export.arxiv.org/api/query?"
    params = f"search_query=all:{query}&start=0&max_results={max_results}"
    
    try:
        response = requests.get(base_url + params)
        response.raise_for_status()
        root = ET.fromstring(response.content)
        papers = []
        
        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            title = entry.find('{http://www.w3.org/2005/Atom}title').text.strip().replace('\n', ' ')
            summary = entry.find('{http://www.w3.org/2005/Atom}summary').text.strip().replace('\n', ' ')
            
            pdf_url = ""
            for link in entry.findall('{http://www.w3.org/2005/Atom}link'):
                if link.get('title') == 'pdf' or link.get('type') == 'application/pdf':
                    pdf_url = link.get('href')
            
            papers.append({
                "title": title,
                "abstract": summary,
                "pdf_url": pdf_url,
                "source": "arXiv"
            })
        return papers
    except Exception as e:
        print(f"Hata: {e}")
        return []

def extract_text_from_pdf(pdf_url):
    if not pdf_url:
        return None
    try:
        # ArXiv linklerini düzelt
        if "arxiv.org/pdf/" in pdf_url and not pdf_url.endswith(".pdf"):
            pdf_url += ".pdf"
        
        time.sleep(1) # Nezaket beklemesi
        response = requests.get(pdf_url, timeout=20)
        response.raise_for_status()
        
        with fitz.open(stream=io.BytesIO(response.content), filetype="pdf") as doc:
            text = ""
            # Tüm sayfaları oku
            for page in doc:
                text += page.get_text()
            return text
    except Exception as e:
        return f"Metin çıkarılamadı: {str(e)}"