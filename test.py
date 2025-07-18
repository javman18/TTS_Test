

import boto3
import os
import openai
from playsound import playsound

# Configura tu clave de OpenAI
openai.api_key = "YOUR_OPEN_ROUTER_KEY"
openai.api_base = "https://openrouter.ai/api/v1"
# Configura Amazon Polly
polly = boto3.client("polly", region_name="us-east-1")

# === Paso 1: Entrada del usuario ===
user_prompt = input("🗣️  Tú: ")

# === Paso 2: Simulación de la interfaz (directo al LLM) ===

# Simulamos el LLM con OpenAI (puedes usar una respuesta fija si quieres)
def get_llm_response(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="mistralai/mistral-7b-instruct",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"⚠️ Error LLM: {e}")
        return "Lo siento, no pude procesar tu solicitud."

# === Paso 3: Obtener respuesta del LLM ===
llm_response = get_llm_response(user_prompt)
print(f"\n🤖 LLM respondió: {llm_response}")

# === Paso 4: Convertir a audio con Amazon Polly ===
def sintetizar_audio(texto, filename="respuesta.mp3"):
    try:
        ssml_text = f"""
        <speak>
          <amazon:domain name="conversational">
            {texto}
          </amazon:domain>
        </speak>
        """
        response = polly.synthesize_speech(
            Text=ssml_text,
            TextType="ssml",
            OutputFormat="mp3",
            VoiceId="Lucia",
            Engine="neural"
        )
        with open(filename, "wb") as f:
            f.write(response["AudioStream"].read())
        print("🔊 Audio generado con éxito.")
    except Exception as e:
        print(f"⚠️ Error al generar audio: {e}")


sintetizar_audio(llm_response)

# === Paso 5: Reproducir audio ===
print("🎧 Reproduciendo audio...")
playsound("respuesta.mp3")
