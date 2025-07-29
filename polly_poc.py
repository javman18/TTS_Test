import boto3
import openai
import os
import platform
from datetime import datetime
from playsound import playsound

# === Configuración de APIs ===
OPENROUTER_API_KEY = "OPENROUTER_KEY"
openai.api_key = OPENROUTER_API_KEY
openai.api_base = "https://openrouter.ai/api/v1"

# Configura Polly
polly = boto3.client("polly", region_name="us-east-1")

# Diccionario emoción español → estilo SSML (emulado)
emotion_map = {
    "alegría": "conversational",
    "serenidad": "conversational",
    "tristeza": "newscaster",
    "ira": "newscaster",
    "confianza": "conversational",
    "miedo": "newscaster",
    "sorpresa": "conversational",
    "decepción": "newscaster",
    "amor": "conversational",
    "remordimiento": "newscaster",
    "optimismo": "conversational",
    "furia": "newscaster",
    "interés": "conversational",
    "melancolía": "newscaster"
    # Puedes expandir más según gusto
}

# === LLM para generar respuesta ===
def get_llm_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="meta-llama/llama-3-8b-instruct",
            messages=[
                {"role": "system", "content": "Responde como un amigo mexicano relajado. Usa lenguaje informal, haz chistes cortos, no expliques cosas innecesarias."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ Error LLM: {e}")
        return "Lo siento, no pude procesar tu solicitud."

# === Generar audio con Polly usando SSML ===
def sintetizar_audio(texto, emotion_ssml="conversational", filename="respuesta.mp3"):
    try:
        ssml = f"<speak>{texto}</speak>"

        response = polly.synthesize_speech(
            Text=ssml,
            TextType="ssml",
            OutputFormat="mp3",
            VoiceId="Lucia",
            Engine="neural"
        )
        with open(filename, "wb") as f:
            f.write(response["AudioStream"].read())
        print(f"🔊 Audio generado con éxito: {filename}")
    except Exception as e:
        print(f"❌ Error Polly: {e}")

# === Bucle principal ===
print("🟢 Escribe lo que quieras. Polly leerá la respuesta con la emoción que elijas (escribe 'salir')")

while True:
    user_prompt = input("\n🧑 Tú: ").strip()
    if user_prompt.lower() in ["salir", "exit", "quit"]:
        break

    emotion_es = input("🎭 ¿Con qué emoción? (feliz, triste, ira, etc.): ").strip().lower()
    emotion_ssml = emotion_map.get(emotion_es, "conversational")

    # Obtener respuesta textual
    respuesta = get_llm_response(user_prompt)
    print(f"🤖 LLM: {respuesta}")

    # Guardar archivo
    file_name = f"respuesta_{emotion_es}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
    sintetizar_audio(respuesta, emotion_ssml, file_name)

    # Reproducir audio
    system_os = platform.system()
    try:
        if system_os == "Darwin":
            os.system(f"afplay {file_name}")
        elif system_os == "Windows":
            os.system(f'start /min wmplayer "{file_name}"')
        else:
            playsound(file_name)
    except Exception as e:
        print(f"🎧 Error al reproducir audio: {e}")
