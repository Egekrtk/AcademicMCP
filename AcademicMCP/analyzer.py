import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-pro')

def analyze_research_with_gemini(topic, papers):
    context = ""
    for i, p in enumerate(papers):
        content = p.get('full_text') if p.get('full_text') else p.get('abstract')
        context += f"\n--- [KAYNAK {i+1}]: {p['title']} ---\n{content}\n"

    prompt = f"""
    Sen uzman bir akademik asistansın. Kullanıcıyla bir chat ortamındaymış gibi konuş.
    Konu: {topic}

    GÖREVİN:
    1. Aşağıdaki makaleleri derinlemesine analiz et.
    2. Yanıtını bir sohbet akışında ver, doğrudan ve samimi ama profesyonel ol.
    3. ÖNEMLİ: Bilgi verirken mutlaka hangi makaleden aldığını [Kaynak X] şeklinde belirt.
    4. Makalelerden doğrudan çarpıcı alıntılar (quotes) yap ve bunları vurgula.
    5. Cevabın sonunda bu çalışmanın sana ne kattığını özetle.

    VERİLER:
    {context}
    """

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Analiz sırasında hata oluştu: {str(e)}"