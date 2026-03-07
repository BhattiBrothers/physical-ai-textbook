---
sidebar_position: 3
---

# Voice Interface Implementation

This lesson covers building a real-time voice interface for humanoid robots using OpenAI Whisper for speech recognition and integrating it with ROS 2 for command execution.

## Architecture Overview

```
Microphone
    │
    ▼
Audio Capture (sounddevice)
    │
    ▼
Whisper STT (speech-to-text)
    │
    ▼
Intent Classification (LLM)
    │
    ▼
ROS 2 Action Publisher
    │
    ▼
Robot Execution
    │
    ▼
TTS Response (text-to-speech)
    │
    ▼
Speaker Output
```

## Setting Up Whisper

```bash
# Install dependencies
pip install openai-whisper sounddevice pyaudio webrtcvad

# Download Whisper model (first run auto-downloads)
# Models: tiny, base, small, medium, large
# base = good balance of speed and accuracy for robotics
python -c "import whisper; whisper.load_model('base')"
```

## Real-Time Voice Activity Detection

Voice Activity Detection (VAD) filters silence so Whisper only processes actual speech:

```python
import sounddevice as sd
import numpy as np
import webrtcvad
import collections
import queue
import threading

class VoiceActivityDetector:
    """
    WebRTC VAD-based voice activity detector.
    Only passes audio frames containing speech to the STT engine.
    """
    def __init__(self, sample_rate: int = 16000, aggressiveness: int = 2):
        self.sample_rate = sample_rate
        self.vad = webrtcvad.Vad(aggressiveness)  # 0 (lenient) to 3 (strict)
        self.frame_duration_ms = 30  # 30 ms frames (VAD requirement)
        self.frame_size = int(sample_rate * self.frame_duration_ms / 1000)

        # Ring buffer to detect speech start
        self.ring_buffer = collections.deque(maxlen=30)  # ~900 ms
        self.triggered = False
        self.voiced_frames = []

        self.audio_queue = queue.Queue()

    def is_speech(self, frame: bytes) -> bool:
        return self.vad.is_speech(frame, self.sample_rate)

    def process_frame(self, frame: np.ndarray) -> bytes | None:
        """
        Process one audio frame.
        Returns complete utterance bytes when speech ends, else None.
        """
        frame_bytes = (frame * 32768).astype(np.int16).tobytes()
        is_speech = self.is_speech(frame_bytes)

        if not self.triggered:
            self.ring_buffer.append((frame_bytes, is_speech))
            num_voiced = sum(1 for _, speech in self.ring_buffer if speech)

            # Start recording when > 60% of ring buffer is speech
            if num_voiced > 0.6 * self.ring_buffer.maxlen:
                self.triggered = True
                self.voiced_frames = [f for f, _ in self.ring_buffer]
                self.ring_buffer.clear()
        else:
            self.voiced_frames.append(frame_bytes)
            self.ring_buffer.append((frame_bytes, is_speech))
            num_unvoiced = sum(1 for _, speech in self.ring_buffer if not speech)

            # Stop recording when > 90% of ring buffer is silence
            if num_unvoiced > 0.9 * self.ring_buffer.maxlen:
                self.triggered = False
                utterance = b''.join(self.voiced_frames)
                self.voiced_frames = []
                self.ring_buffer.clear()
                return utterance

        return None
```

## Whisper Speech-to-Text

```python
import whisper
import numpy as np
import io
import soundfile as sf

class WhisperSTT:
    """
    OpenAI Whisper speech-to-text engine.
    Supports multiple languages including Urdu.
    """

    def __init__(self, model_size: str = "base", language: str = "en"):
        print(f"Loading Whisper {model_size} model...")
        self.model = whisper.load_model(model_size)
        self.language = language
        self.sample_rate = 16000
        print("Whisper ready!")

    def transcribe(self, audio_bytes: bytes) -> dict:
        """
        Transcribe audio bytes to text.
        Returns dict with 'text', 'language', 'confidence'.
        """
        # Convert bytes to numpy array
        audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32)
        audio_np = audio_np / 32768.0  # Normalize to [-1, 1]

        result = self.model.transcribe(
            audio_np,
            language=self.language,
            task="transcribe",
            fp16=False,  # Use FP32 for CPU compatibility
            verbose=False
        )

        return {
            "text": result["text"].strip(),
            "language": result.get("language", self.language),
            "segments": result.get("segments", [])
        }

    def transcribe_multilingual(self, audio_bytes: bytes) -> dict:
        """Auto-detect language (useful for multilingual robots)."""
        audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32)
        audio_np = audio_np / 32768.0

        # Detect language first
        mel = whisper.log_mel_spectrogram(audio_np)
        _, probs = self.model.detect_language(mel)
        detected_lang = max(probs, key=probs.get)

        result = self.model.transcribe(audio_np, language=detected_lang)
        return {"text": result["text"].strip(), "language": detected_lang}
```

## Intent Classification with LLM

```python
from openai import OpenAI
import json

class RobotIntentClassifier:
    """
    Uses GPT to classify voice commands into structured robot actions.
    """

    SYSTEM_PROMPT = """You are an intent classifier for a humanoid robot.
Convert natural language commands into structured JSON actions.

Available actions:
- navigate: Move to a location {"action": "navigate", "location": "kitchen"}
- pick: Pick up an object {"action": "pick", "object": "cup"}
- place: Put object somewhere {"action": "place", "object": "cup", "destination": "table"}
- wave: Wave hand {"action": "wave"}
- stop: Emergency stop {"action": "stop"}
- status: Report robot status {"action": "status"}
- unknown: Unrecognized command {"action": "unknown", "raw": "original text"}

Respond ONLY with valid JSON. No explanation."""

    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)

    def classify(self, text: str) -> dict:
        """Classify text command into structured action."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # Fast and cheap for classification
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": f"Command: {text}"}
                ],
                temperature=0.1,
                max_tokens=100
            )

            raw = response.choices[0].message.content
            return json.loads(raw)

        except json.JSONDecodeError:
            return {"action": "unknown", "raw": text}
        except Exception as e:
            return {"action": "error", "message": str(e)}
```

## ROS 2 Voice Command Node

```python
import rclpy
from rclpy.node import Node
from std_msgs.msg import String
from geometry_msgs.msg import PoseStamped
import sounddevice as sd
import numpy as np
import threading
import queue
import os

class VoiceCommandNode(Node):
    """
    ROS 2 node that listens for voice commands and publishes robot actions.
    """

    def __init__(self):
        super().__init__('voice_command_node')

        # Publishers
        self.command_pub = self.create_publisher(String, '/voice_commands', 10)
        self.status_pub = self.create_publisher(String, '/robot_status', 10)

        # Services and config
        self.declare_parameter('whisper_model', 'base')
        self.declare_parameter('language', 'en')
        self.declare_parameter('openai_api_key', '')

        model_size = self.get_parameter('whisper_model').value
        language = self.get_parameter('language').value
        api_key = self.get_parameter('openai_api_key').value or os.environ.get('OPENAI_API_KEY', '')

        # Initialize components
        self.stt = WhisperSTT(model_size, language)
        self.classifier = RobotIntentClassifier(api_key) if api_key else None
        self.vad = VoiceActivityDetector()

        self.audio_queue = queue.Queue()
        self.is_listening = True

        # Start audio capture thread
        self.audio_thread = threading.Thread(
            target=self._capture_audio, daemon=True
        )
        self.audio_thread.start()

        # Processing timer
        self.timer = self.create_timer(0.03, self._process_audio)

        self.get_logger().info(
            f'Voice interface ready (Whisper: {model_size}, Lang: {language})'
        )

    def _capture_audio(self):
        """Continuously capture audio in background thread."""
        with sd.InputStream(
            samplerate=16000,
            channels=1,
            dtype='float32',
            blocksize=480,   # 30 ms @ 16kHz
            callback=self._audio_callback
        ):
            while self.is_listening:
                sd.sleep(100)

    def _audio_callback(self, indata, frames, time, status):
        self.audio_queue.put(indata[:, 0].copy())

    def _process_audio(self):
        """Process queued audio frames."""
        frames = []
        while not self.audio_queue.empty():
            frames.append(self.audio_queue.get_nowait())

        if not frames:
            return

        audio_chunk = np.concatenate(frames)
        utterance = self.vad.process_frame(audio_chunk)

        if utterance:
            self._handle_utterance(utterance)

    def _handle_utterance(self, audio_bytes: bytes):
        """Transcribe and classify a complete utterance."""
        self.get_logger().info('Processing voice command...')

        # Transcribe
        result = self.stt.transcribe(audio_bytes)
        text = result["text"]

        if not text:
            return

        self.get_logger().info(f'Heard: "{text}"')

        # Classify intent
        if self.classifier:
            intent = self.classifier.classify(text)
            self.get_logger().info(f'Intent: {intent}')
        else:
            intent = {"action": "unknown", "raw": text}

        # Publish command
        msg = String()
        msg.data = str(intent)
        self.command_pub.publish(msg)

def main():
    rclpy.init()
    node = VoiceCommandNode()
    rclpy.spin(node)
    rclpy.shutdown()

if __name__ == '__main__':
    main()
```

## Text-to-Speech (Robot Feedback)

```python
import subprocess
import tempfile
import os

class RobotVoice:
    """Give the robot a voice using TTS."""

    def speak(self, text: str, lang: str = "en"):
        """Speak text using espeak or pyttsx3."""
        try:
            # espeak — available on most Linux systems
            subprocess.run(
                ["espeak", f"-v{lang}", "-s150", text],
                check=True,
                capture_output=True
            )
        except FileNotFoundError:
            # Fallback: pyttsx3
            import pyttsx3
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.say(text)
            engine.runAndWait()

# Usage
voice = RobotVoice()
voice.speak("I am ready to receive commands.")
voice.speak("Moving to the kitchen now.")
```

## Complete Voice Pipeline

```python
def run_voice_pipeline():
    """Complete voice-to-action pipeline."""
    stt = WhisperSTT(model_size="base")
    classifier = RobotIntentClassifier(api_key=os.environ["OPENAI_API_KEY"])
    voice = RobotVoice()
    vad = VoiceActivityDetector()

    print("Listening... (say a command)")

    with sd.InputStream(samplerate=16000, channels=1, dtype='float32', blocksize=480) as stream:
        while True:
            audio_chunk, _ = stream.read(480)
            utterance = vad.process_frame(audio_chunk[:, 0])

            if utterance:
                # Transcribe
                result = stt.transcribe(utterance)
                text = result["text"]
                print(f"You said: {text}")

                # Classify
                intent = classifier.classify(text)
                print(f"Intent: {intent}")

                # Acknowledge
                voice.speak(f"Understood. Executing {intent.get('action', 'command')}.")

                # Execute (would call ROS 2 actions here)
                execute_intent(intent)

def execute_intent(intent: dict):
    """Map classified intent to robot actions."""
    action = intent.get("action")

    if action == "navigate":
        location = intent.get("location", "")
        print(f"Navigating to: {location}")
        # ros2 navigate_to(location)

    elif action == "pick":
        obj = intent.get("object", "")
        print(f"Picking up: {obj}")
        # ros2 pick_object(obj)

    elif action == "stop":
        print("EMERGENCY STOP!")
        # ros2 emergency_stop()

    elif action == "wave":
        print("Waving...")
        # ros2 wave_hand()
```

## Exercises

1. Set up Whisper and record yourself saying 5 robot commands — check transcription accuracy
2. Build the intent classifier and test it with ambiguous commands like "go there" or "pick that up"
3. Integrate the voice node with your Nav2 setup from Module 3 to navigate by voice
4. Add Urdu language support by changing `language="ur"` in WhisperSTT
