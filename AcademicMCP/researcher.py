import requests
import xml.etree.ElementTree as ET
import fitz
import io
import time

def search_arxiv(query, max_results=3):
    # ArXiv Türkçe anlamaz, bu yüzden sorguyu temizleyip anahtar kelimelere odaklanıyoruz.
    # Eğer kullanıcı Türkçe yazarsa, sistem temel anahtar kelimeleri seçmeye çalışır.
    # Tavsiye: Kullanıcıya İngilizce arama yapmasını hatırlatabilirsin.
    
    clean_query = query.replace("istiyorum", "").replace("yapmak", "").replace("hakkında", "")
    
    base_url = "http://export.arxiv.org/api/query?"
    # Arama parametresini daha spesifik hale getirdik
    params = f"search_query=all:{clean_query}&start=0&max_results={max_results}&sortBy=relevance"
    
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
            
            # Eğer link /abs/ ise /pdf/'e çevir
            if pdf_url and "/abs/" in pdf_url:
                pdf_url = pdf_url.replace("/abs/", "/pdf/")

            papers.append({
                "title": title,
                "abstract": summary,
                "pdf_url": pdf_url
            })
        return papers
    except Exception as e:
        print(f"ArXiv Hatası: {e}")
        return []

def extract_text_from_pdf(pdf_url):
    if not pdf_url: return None
    try:
        if not pdf_url.endswith(".pdf"): pdf_url += ".pdf"
        
        response = requests.get(pdf_url, timeout=15)
        with fitz.open(stream=io.BytesIO(response.content), filetype="pdf") as doc:
            text = ""
            # Render ücretsiz planında CPU limitine takılmamak için 
            # tüm sayfalar yerine ilk 15 sayfayı alalım (genelde yeterlidir)
            for page in doc[:15]:
                text += page.get_text()
            return text
    except Exception as e:
        return f"PDF Okuma Hatası: {str(e)}"