import google.generativeai as genai
import os # Sistem değişkenlerine erişmek için gerekli
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("HATA: GEMINI_API_KEY bulunamadı! Lütfen ortam değişkenlerini kontrol edin.")
else:
    genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-1.5-pro')

def analyze_research_with_gemini(topic, papers):
    """
    ArXiv'den gelen makale listesini Gemini'ye analiz ettirir.
    """
    combined_content = ""
    for p in papers:
        # researcher.py'den gelen veriyi metne ekle
        text_to_analyze = p.get('full_text') if p.get('full_text') else p.get('abstract')
        combined_content += f"\n---\nBAŞLIK: {p['title']}\nİÇERİK: {text_to_analyze}\n"

    # Gemini'ye gidecek olan talimat (Prompt)
    prompt = f"""
    Sen uzman bir akademik araştırmacısın. Konu: {topic}
    Aşağıdaki makale içeriklerini derinlemesine analiz et:
    
    1. Bu konunun bilimsel önemini ve neden güncel olduğunu açıkla.
    2. Makalelerdeki ortak argümanları ve birbirlerinden ayrıldıkları noktaları belirt.
    3. Bu makaleler arasındaki ilişkiyi bir 'Bilgi Haritası' (Knowledge Graph) şeklinde 
       sunabilmem için bana sadece JSON formatında 'nodes' (makale başlıkları) ve 
       'edges' (bağlantı nedenleri) listesi ver.
    
    Veriler:
    {combined_content}
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Gemini Analiz Hatası: {str(e)}"