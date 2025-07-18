


from google import genai
from google.genai import types
import wave, os
from datetime import datetime
import boto3
import openai
import platform


# === Configuración de APIs ===
GENAI_API_KEY = "YOUR_GEMINI_KEY"
OPENROUTER_API_KEY = "YOUR_OPEN_ROUTER_KEY"

# OpenRouter
openai.api_key = OPENROUTER_API_KEY
openai.api_base = "https://openrouter.ai/api/v1"

# Gemini TTS
client = genai.Client(api_key=GENAI_API_KEY)

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
print("🟢 Escribe lo que quieras. Gemini leerá la respuesta del LLM (escribe 'salir')")

while True:
    user_prompt = input("🧑 Tú: ")
    if user_prompt.lower() in ["salir", "exit", "quit"]:
        break

    try:
        # Obtener respuesta textual del LLM
        llm_response = get_llm_response(user_prompt)
        print(f"🤖 LLM: {llm_response}")

        # Enviar esa respuesta al modelo TTS de Gemini
        tts_response = client.models.generate_content(
            model="gemini-2.5-flash-preview-tts",
            contents=llm_response,
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

        # Extraer y guardar audio
        audio_data = tts_response.candidates[0].content.parts[0].inline_data.data
        file_name = f"respuesta_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        wave_file(file_name, audio_data)
        print(f"🔊 Audio guardado como: {file_name}")
        # Reproducir el audio según el sistema operativo
        system_os = platform.system()
        if system_os == "Darwin":  # macOS
            os.system(f"afplay {file_name}")
        elif system_os == "Windows":
            os.system(f'start /min wmplayer "{file_name}"')  # Usa Windows Media Player
        else:
            print("🔇 No se puede reproducir audio automáticamente en este sistema.")


    except Exception as e:
        print("❌ Error:", e)
