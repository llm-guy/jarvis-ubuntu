## Jarvis Voice Assistant (Ubuntu Version)

Jarvis is a voice-activated AI assistant that listens for a wake word (“Jarvis”), processes voice commands using a local LLM (Ollama + Qwen), and can control smart devices through Home Assistant.

This version is optimized to run on Ubuntu Linux with no cloud services required.

# Requirements

Ubuntu 20.04+ / 22.04+

Working microphone and speakers

Internet only for installation (model download)

Python 3.10+

Ollama (auto-installed)

# Installation 

Open a terminal and run

```
git clone https://github.com/llm-guy/jarvis-ubuntu
cd jarvis-ubuntu
chmod +x install.sh run.sh
./install.sh
```

# Running Jarvis

After Installation 

```
./run.sh
```

Jarvis will:

1. Calibrate the microphone

2. Listen for the wake word: "Jarvis"

3. Process your command

4. Speak the response

To stop Jarvis:
Press CTRL + C in the terminal.


