
from google import genai

client = genai.Client(api_key="YOUR_GEMINI_KEY")

models = client.models.list()

tts_models = [m.name for m in models if "tts" in m.name or "audio" in m.name]
print("Modelos TTS disponibles con tu key:\n", "\n".join(tts_models))

import openai

openai.api_key = "YOUR_OPEN_ROUTER_KEY"
openai.api_base = "https://openrouter.ai/api/v1"

models = openai.Model.list()

print("📦 Modelos disponibles en tu cuenta de OpenRouter:\n")
for m in models['data']:
    print("-", m['id'])
