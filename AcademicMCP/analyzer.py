import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)

# Model adını 'gemini-1.5-flash' yaparak daha geniş uyumluluk sağlıyoruz
model = genai.GenerativeModel('gemini-1.5-flash')

def analyze_research_with_gemini(topic, papers):
    if not papers:
        return "Arama sonucunda analiz edilecek makale bulunamadı."

    context = ""
    for i, p in enumerate(papers):
        # Full text varsa al, yoksa abstract kullan
        content = p.get('full_text') if p.get('full_text') else p.get('abstract', 'İçerik yok.')
        context += f"\n--- [KAYNAK {i+1}]: {p['title']} ---\n{content[:15000]}\n" # Bellek sınırı için kırpma

    prompt = f"""
    Sen uzman bir akademik asistansın. Konu: {topic}

    GÖREVİN:
    1. Aşağıdaki makaleleri derinlemesine analiz et.
    2. Yanıtını bir sohbet akışında ver. Bilgi verirken mutlaka [Kaynak X] şeklinde belirt.
    3. Makalelerden doğrudan çarpıcı alıntılar (quotes) yap.
    4. Teknik terimleri açıkla ve kullanıcının sorusuna (Trade Bot mimarisi vb.) odaklan.

    VERİLER:
    {context}
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        # Hatanın detayını frontend'e gönderiyoruz
        return f"Gemini Analiz Hatası: {str(e)}"