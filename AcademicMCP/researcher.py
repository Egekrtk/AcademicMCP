import requests
import xml.etree.ElementTree as ET
import fitz  # PyMuPDF
import io
import time

def search_arxiv(query, max_results=5):
    base_url = "http://export.arxiv.org/api/query?"
    params = f"search_query=all:{query}&start=0&max_results={max_results}"
    
    try:
        response = requests.get(base_url + params)
        response.raise_for_status()
        
        root = ET.fromstring(response.content)
        papers = []
        
        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            title = entry.find('{http://www.w3.org/2005/Atom}title').text
            summary = entry.find('{http://www.w3.org/2005/Atom}summary').text
            published = entry.find('{http://www.w3.org/2005/Atom}published').text
            
            authors = [auth.find('{http://www.w3.org/2005/Atom}name').text 
                       for auth in entry.findall('{http://www.w3.org/2005/Atom}author')]
            
            pdf_url = ""
            for link in entry.findall('{http://www.w3.org/2005/Atom}link'):
                if link.get('title') == 'pdf':
                    pdf_url = link.get('href')
                # Bazen title='pdf' olmayabilir, 'type' kontrolü ekleyelim
                elif link.get('type') == 'application/pdf':
                    pdf_url = link.get('href')
            
            papers.append({
                "title": title.strip().replace('\n', ' '),
                "abstract": summary.strip().replace('\n', ' '),
                "authors": authors,
                "year": published[:4],
                "pdf_url": pdf_url,
                "source": "arXiv"
            })
            
        return papers
    except Exception as e:
        print(f"ArXiv araması sırasında hata oluştu: {e}")
        return []

def extract_text_from_pdf(pdf_url):
    if not pdf_url:
        return None
        
    try:
        # ArXiv bazen /pdf/ kısmına yönlendirir, URL'yi kontrol et
        if not pdf_url.endswith(".pdf") and "arxiv.org/pdf/" not in pdf_url:
            pdf_url += ".pdf"

        time.sleep(1) 
        response = requests.get(pdf_url, timeout=15)
        response.raise_for_status()
        
        with fitz.open(stream=io.BytesIO(response.content), filetype="pdf") as doc:
            text = ""
            # İlk 5 sayfa genellikle en kritik kısımdır
            for page in doc[:5]:
                text += page.get_text()
            return text
    except Exception as e:
        return f"PDF metni çıkarılamadı: {str(e)}"