


from google import genai
from google.genai import types
import wave, os
from datetime import datetime
import boto3
import openai
import platform


# === Configuración de APIs ===
GENAI_API_KEY = "AIzaSyDigHn9Ys2GjOu3HFxcCQqXsoq_5wLZ6Lw"
OPENROUTER_API_KEY = "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"

# OpenRouter
openai.api_key = OPENROUTER_API_KEY
openai.api_base = "https://openrouter.ai/api/v1"

# Gemini TTS
client = genai.Client(api_key=GENAI_API_KEY)

# Diccionario emoción español → inglés
emotion_map = {
    # Alegría
    "alegría": "happily",
    "éxtasis": "ecstatically",
    "serenidad": "calmly",
    
    # Confianza
    "confianza": "confidently",
    "admiración": "respectfully",
    "aprobación": "supportively",

    # Miedo
    "miedo": "fearfully",
    "temor": "nervously",
    "terror": "terrified",

    # Sorpresa
    "sorpresa": "surprised",
    "asombro": "astonished",
    "distracción": "curiously",

    # Tristeza
    "tristeza": "sadly",
    "pena": "sorrowfully",
    "melancolía": "melancholically",

    # Disgusto
    "aversión": "disgusted",
    "odio": "hateful",
    "tedio": "bored",

    # Ira
    "ira": "angrily",
    "furia": "furiously",
    "enfado": "annoyed",

    # Anticipación
    "interés": "interested",
    "anticipación": "expectantly",
    "vigilancia": "alertly",

    # Combinadas 
    "amor": "lovingly",
    "optimismo": "optimistically",
    "sumisión": "submissively",
    "desprecio": "disdainfully",
    "alevosía": "maliciously",
    "remordimiento": "regretfully",
    "decepción": "disappointed",
    "susto": "shocked"
}


# === Función para obtener respuesta del LLM ===
def get_llm_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="meta-llama/llama-3-8b-instruct",
            messages=[
                {"role": "system", "content": "Responde como un amigo mexicano relajado. Usa lenguaje informal, haz chistes cortos, no expliques cosas innecesarias. Si el usuario dice 'jaja' o no entiende, responde de forma divertida o con otro chiste."},
                {"role": "user", "content": prompt}
            ]

        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ Error LLM: {e}")
        return "Lo siento, no pude procesar tu solicitud."

# === Guardar audio en WAV ===
def wave_file(filename, pcm, channels=1, rate=24000, sample_width=2):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm)

# === Ciclo interactivo ===
print("🟢 Escribe lo que quieras. Gemini leerá la respuesta del LLM con la emoción que elijas (escribe 'salir')")

while True:
    user_prompt = input("🧑 Tú: ")
    if user_prompt.lower() in ["salir", "exit", "quit"]:
        break

    emotion_es = input("🎭 ¿Con qué emoción? (feliz, triste, enojado, etc.): ").strip().lower()
    emotion_en = emotion_map.get(emotion_es, "neutrally")

    try:
        # 1. Obtener respuesta textual
        llm_response = get_llm_response(user_prompt)
        print(f"🤖 LLM: {llm_response}")

        # 2. Enviar esa respuesta al modelo TTS de Gemini
        tts_response = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=f"say {emotion_en}: {llm_response}",
            config=types.GenerateContentConfig(
                response_modalities=["AUDIO"],
                speech_config=types.SpeechConfig(
                    voice_config=types.VoiceConfig(
                        prebuilt_voice_config=types.PrebuiltVoiceConfig(
                            voice_name='Zubenelgenubi'
                        )
                    )
                ),
            )
        )

        # 3. Extraer y guardar audio
        audio_data = tts_response.candidates[0].content.parts[0].inline_data.data
        file_name = f"respuesta_{emotion_es}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        wave_file(file_name, audio_data)
        print(f"🔊 Audio guardado como: {file_name}")

        # 4. Reproducir el audio según el sistema operativo
        system_os = platform.system()
        if system_os == "Darwin":  # macOS
            os.system(f"afplay {file_name}")
        elif system_os == "Windows":
            os.system(f'start /min wmplayer "{file_name}"')
        else:
            print("🔇 No se puede reproducir audio automáticamente en este sistema.")

    except Exception as e:
        print(f"❌ Error: {e}")