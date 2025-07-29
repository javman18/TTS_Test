from elevenlabs.client import ElevenLabs
from elevenlabs import play, save, VoiceSettings
import openai
import os
from datetime import datetime
import platform

# === Configuración de APIs ===
OPENROUTER_API_KEY = "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"
ELEVENLABS_API_KEY = "sk_10d8dabaef70daf91e184c38615eea3f4816b0ed395ab8b0"

# OpenRouter (LLM)
openai.api_key = OPENROUTER_API_KEY
openai.api_base = "https://openrouter.ai/api/v1"

# ElevenLabs (TTS)
elevenlabs = ElevenLabs(api_key=ELEVENLABS_API_KEY)

# === Diccionario emoción español → inglés para ElevenLabs (como next_text) ===
emotion_map = {
    "alegría": "said happily",
    "éxtasis": "said ecstatically",
    "serenidad": "said calmly",
    "confianza": "said confidently",
    "admiración": "said respectfully",
    "aprobación": "said supportively",
    "miedo": "said fearfully",
    "temor": "said nervously",
    "terror": "said terrified",
    "sorpresa": "said surprised",
    "asombro": "said astonished",
    "distracción": "said curiously",
    "tristeza": "said sadly",
    "pena": "said sorrowfully",
    "melancolía": "said melancholically",
    "aversión": "said disgusted",
    "odio": "said hatefully",
    "tedio": "said bored",
    "ira": "said angrily",
    "furia": "said furiously",
    "enfado": "said annoyed",
    "interés": "said interested",
    "anticipación": "said expectantly",
    "vigilancia": "said alertly",
    "amor": "said lovingly",
    "optimismo": "said optimistically",
    "sumisión": "said submissively",
    "desprecio": "said disdainfully",
    "alevosía": "said maliciously",
    "remordimiento": "said regretfully",
    "decepción": "said disappointed",
    "susto": "said shocked"
}


# === Historial de conversación ===
conversation_history = [
    {"role": "system", "content": "Responde como un amigo mexicano relajado. Usa lenguaje informal, haz chistes cortos, no expliques cosas innecesarias. Si el usuario dice 'jaja' o no entiende, responde de forma divertida o con otro chiste."}
]

# === Obtener respuesta del LLM con contexto ===
def get_llm_response(prompt):
    conversation_history.append({"role": "user", "content": prompt})
    try:
        response = openai.ChatCompletion.create(
            model="meta-llama/llama-3-8b-instruct",
            messages=conversation_history
        )
        reply = response.choices[0].message.content.strip()
        conversation_history.append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        print(f"⚠️ Error LLM: {e}")
        return "Lo siento, no pude procesar tu solicitud."

# === Ciclo interactivo ===
print("🟢 Escribe lo que quieras. ElevenLabs leerá la respuesta con emoción (escribe 'salir')")

while True:
    user_prompt = input("🧑 Tú: ")
    if user_prompt.lower() in ["salir", "exit", "quit"]:
        break

    emotion_es = input("🎭 ¿Con qué emoción? (feliz, triste, enojado, etc.): ").strip().lower()
    emotion_tag = emotion_map.get(emotion_es, "said neutrally")


    try:
        # 1. Obtener respuesta textual
        llm_response = get_llm_response(user_prompt)
        print(f"🤖 LLM: {llm_response}")

        # 2. Generar audio con ElevenLabs
        audio = elevenlabs.text_to_speech.convert(
            voice_id="bkntBQwrjzsp6mDDVjkG",  # Cambia si quieres otra voz
            text=llm_response,
            model_id="eleven_multilingual_v2",
            voice_settings=VoiceSettings(
                stability=0.3,
                similarity_boost=0.75,
                use_speaker_boost=True,
            ),
            next_text=emotion_tag,
            output_format="mp3_44100_128",
        )

        # 3. Guardar audio
        file_name = f"respuesta_{emotion_es}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        save(audio, file_name)
        print(f"🔊 Audio guardado como: {file_name}")

        # 4. Reproducir audio según el sistema
        system_os = platform.system()
        if system_os == "Darwin":
            os.system(f"afplay {file_name}")
        elif system_os == "Windows":
            os.system(f'start /min wmplayer "{file_name}"')
        else:
            print("🔇 No se puede reproducir automáticamente en este sistema.")

    except Exception as e:
        print(f"❌ Error: {e}")
