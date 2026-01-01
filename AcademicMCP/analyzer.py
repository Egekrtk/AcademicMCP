import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("HATA: GEMINI_API_KEY bulunamadı!")
else:
    genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-1.5-pro')

def analyze_research_with_gemini(topic, papers):
    combined_content = ""
    for p in papers:
        # Eğer full_text varsa onu, yoksa abstract'ı kullan
        text_to_analyze = p.get('full_text') if p.get('full_text') else p.get('abstract')
        combined_content += f"\n---\nBAŞLIK: {p['title']}\nİÇERİK: {text_to_analyze}\n"

    prompt = f"""
    Sen uzman bir akademik araştırmacısın. Konu: {topic}
    Aşağıdaki makale içeriklerini derinlemesine analiz et:
    
    1. Bu konunun bilimsel önemini ve neden güncel olduğunu açıkla.
    2. Makalelerdeki ortak argümanları ve birbirlerinden ayrıldıkları noktaları belirt.
    3. Bilgi Haritası (Knowledge Graph) için: Makaleler arasındaki ilişkiyi 
       sadece JSON formatında (```json ... ``` blokları içinde) 'nodes' ve 'edges' olarak ver.
    
    Veriler:
    {combined_content}
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gemini Analiz Hatası: {str(e)}"