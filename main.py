import os
import logging
import time

import pyttsx3
from dotenv import load_dotenv
import speech_recognition as sr
from langchain_ollama import ChatOllama
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate

# importing tools
from tools.time_tool import get_time
from tools.HA import toggle_office_light

# Load environment variables from .env if present
load_dotenv()

# ---- Configuration ----
MIC_INDEX_ENV = os.getenv("MIC_INDEX", "").strip()
MIC_INDEX = int(MIC_INDEX_ENV) if MIC_INDEX_ENV else None

TRIGGER_WORD = os.getenv("TRIGGER_WORD", "jarvis")
CONVERSATION_TIMEOUT = int(os.getenv("CONVERSATION_TIMEOUT", "30"))

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

recognizer = sr.Recognizer()
mic = sr.Microphone(device_index=MIC_INDEX)

# ---- LLM Setup ----
llm = ChatOllama(model="qwen3:1.7b", reasoning=False)

# Tool list
tools = [get_time, toggle_office_light]

# Tool-calling prompt
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are Jarvis, an intelligent, conversational AI assistant. "
            "Your goal is to be helpful, friendly, and informative. You can respond "
            "in natural, human-like language and use tools when needed to answer "
            "questions more accurately. Always explain your reasoning simply when "
            "appropriate, and keep your responses conversational and concise.",
        ),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

# Agent + executor
agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

# ---- TTS Setup (Linux-friendly) ----
# Initialize the engine once (much faster & more stable)
_tts_engine = pyttsx3.init()
_tts_engine.setProperty("rate", 180)
_tts_engine.setProperty("volume", 1.0)

# Try to pick a reasonable English voice on Linux (espeak)
voices = _tts_engine.getProperty("voices")
selected_voice_id = None

# If the user sets a preferred voice via env, respect that
PREFERRED_VOICE = os.getenv("TTS_VOICE_NAME", "").lower().strip()

if voices:
    if PREFERRED_VOICE:
        # Try to match the env-provided voice name
        for v in voices:
            if PREFERRED_VOICE in v.name.lower():
                selected_voice_id = v.id
                break
    if not selected_voice_id:
        # Fallback: try to pick an English voice
        for v in voices:
            if "english" in v.name.lower():
                selected_voice_id = v.id
                break
    if selected_voice_id:
        _tts_engine.setProperty("voice", selected_voice_id)


def speak_text(text: str) -> None:
    """Speak text out loud using pyttsx3 on Ubuntu."""
    try:
        _tts_engine.say(text)
        _tts_engine.runAndWait()
        time.sleep(0.2)
    except Exception as e:
        logging.error(f"❌ TTS failed: {e}")


# ---- Main interaction loop ----
def write():
    conversation_mode = False
    last_interaction_time = None

    try:
        with mic as source:
            recognizer.adjust_for_ambient_noise(source)
            logging.info("🎙 Microphone calibrated for ambient noise.")

            while True:
                try:
                    # Handle conversation timeout
                    if (
                        conversation_mode
                        and last_interaction_time is not None
                        and (time.time() - last_interaction_time) > CONVERSATION_TIMEOUT
                    ):
                        logging.info("⌛ Conversation timeout. Returning to wake-word mode.")
                        conversation_mode = False

                    if not conversation_mode:
                        logging.info("🎤 Listening for wake word...")
                        audio = recognizer.listen(source, timeout=10)
                        transcript = recognizer.recognize_google(audio)
                        logging.info(f"🗣 Heard: {transcript}")

                        if TRIGGER_WORD.lower() in transcript.lower():
                            logging.info(f"🗣 Triggered by: {transcript}")
                            speak_text("Yes, sir?")
                            conversation_mode = True
                            last_interaction_time = time.time()
                        else:
                            logging.debug("Wake word not detected, continuing...")
                    else:
                        logging.info("🎤 Listening for next command...")
                        audio = recognizer.listen(source, timeout=10)
                        command = recognizer.recognize_google(audio)
                        logging.info(f"📥 Command: {command}")

                        logging.info("🤖 Sending command to agent...")
                        response = executor.invoke({"input": command})
                        content = response["output"]
                        logging.info(f"✅ Agent responded: {content}")

                        print("Jarvis:", content)
                        speak_text(content)
                        last_interaction_time = time.time()

                except sr.WaitTimeoutError:
                    logging.warning("⚠️ Timeout waiting for audio.")
                    if (
                        conversation_mode
                        and last_interaction_time is not None
                        and (time.time() - last_interaction_time) > CONVERSATION_TIMEOUT
                    ):
                        logging.info(
                            "⌛ No input in conversation mode. Returning to wake word mode."
                        )
                        conversation_mode = False
                except sr.UnknownValueError:
                    logging.warning("⚠️ Could not understand audio.")
                except Exception as e:
                    logging.error(f"❌ Error during recognition or tool call: {e}")
                    time.sleep(1)

    except Exception as e:
        logging.critical(f"❌ Critical error in main loop: {e}")


if __name__ == "__main__":
    write()
