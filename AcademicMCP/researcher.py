import requests
import xml.etree.ElementTree as ET
import fitz  # PyMuPDF
import io
import time

def search_arxiv(query, max_results=5):
    """
    ArXiv API'sini kullanarak makale arar.
    XML formatındaki sonucu parse eder ve liste olarak döner.
    """
    # ArXiv API URL'si (Atom formatında döner)
    base_url = "http://export.arxiv.org/api/query?"
    # Arama parametreleri: all (her yerde ara), max_results (sonuç sayısı)
    params = f"search_query=all:{query}&start=0&max_results={max_results}"
    
    try:
        response = requests.get(base_url + params)
        response.raise_for_status()
        
        # XML'i parse etme
        root = ET.fromstring(response.content)
        papers = []
        
        # XML içinde 'entry' etiketlerini bul (her biri bir makaledir)
        for entry in root.findall('{http://www.w3.org/2005/Atom}entry'):
            title = entry.find('{http://www.w3.org/2005/Atom}title').text
            summary = entry.find('{http://www.w3.org/2005/Atom}summary').text
            published = entry.find('{http://www.w3.org/2005/Atom}published').text
            
            # Yazarları çekme
            authors = [auth.find('{http://www.w3.org/2005/Atom}name').text 
                       for auth in entry.findall('{http://www.w3.org/2005/Atom}author')]
            
            # PDF linkini bulma
            pdf_url = ""
            for link in entry.findall('{http://www.w3.org/2005/Atom}link'):
                if link.get('title') == 'pdf':
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
    """
    Verilen ArXiv PDF linkinden metni çeker.
    """
    if not pdf_url:
        return None
        
    try:
        # ArXiv'i aşırı yüklememek için kısa bir bekleme (nezaket kuralı)
        time.sleep(1) 
        
        response = requests.get(pdf_url, timeout=15)
        response.raise_for_status()
        
        # PDF dosyasını bellekte aç
        with fitz.open(stream=io.BytesIO(response.content), filetype="pdf") as doc:
            text = ""
            # İlk 5 sayfayı al (Genelde özet, giriş ve metodoloji için yeterlidir)
            for page in doc[:5]:
                text += page.get_text()
            return text
    except Exception as e:
        return f"PDF metni çıkarılamadı: {str(e)}"

# Test için (isteğe bağlı silinebilir)
if __name__ == "__main__":
    test_results = search_arxiv("quantum neural networks", 2)
    for p in test_results:
        print(f"Başlık: {p['title']}\nPDF: {p['pdf_url']}\n---")