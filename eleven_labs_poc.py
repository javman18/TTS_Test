from elevenlabs.client import ElevenLabs
from elevenlabs import play, save, VoiceSettings
import openai
import os
from datetime import datetime
import platform

# === Configuración de APIs ===
OPENROUTER_API_KEY = "YOUR_OPEN_ROUTER_KEY"
ELEVENLABS_API_KEY = "YOUR_ELEVENLABS_KEY"

# OpenRouter (LLM)
openai.api_key = OPENROUTER_API_KEY
openai.api_base = "https://openrouter.ai/api/v1"

# ElevenLabs (TTS)
elevenlabs = ElevenLabs(api_key=ELEVENLABS_API_KEY)


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
print("🟢 Escribe lo que quieras. ElevenLabs leerá la respuesta del LLM (escribe 'salir')")

while True:
    user_prompt = input("🧑 Tú: ")
    if user_prompt.lower() in ["salir", "exit", "quit"]:
        break

    try:
        # 1. Obtener respuesta textual
        llm_response = get_llm_response(user_prompt)
        print(f"🤖 LLM: {llm_response}")

        # 2. Generar audio con ElevenLabs
        audio = elevenlabs.text_to_speech.convert(
            ##text=llm_response,
            voice_id="bkntBQwrjzsp6mDDVjkG",
            text=llm_response,
            model_id="eleven_multilingual_v2",
            voice_settings= VoiceSettings(
                stability= 0.3,
                similarity_boost=0.75,
                use_speaker_boost= True,
            ),
            next_text="dijo asustado",
            output_format="mp3_44100_128",
        )

        # 3. Guardar audio en archivo
        file_name = f"respuesta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        save(audio, file_name)
        print(f"🔊 Audio guardado como: {file_name}")

        # 4. Reproducir audio según sistema operativo
        system_os = platform.system()
        if system_os == "Darwin":
            os.system(f"afplay {file_name}")
        elif system_os == "Windows":
            os.system(f'start /min wmplayer "{file_name}"')
        else:
            print("🔇 No se puede reproducir automáticamente en este sistema.")

    except Exception as e:
        print(f"❌ Error: {e}")
