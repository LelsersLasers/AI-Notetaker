import base64
import os
import whisper
from pydub import AudioSegment
from openai import OpenAI


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


class video_analyzer:
    def __init__(self, video_path, image_base):
        self.vision_prompt = (
            "In the context of a university lecture, describe in detail what is "
            "going on in the picture..."
        )
        self.client = OpenAI()
        self.image_base = image_base
        self.video_path = video_path
        self.whisper_model = whisper.load_model("base")

    def transcribe_video(self):
        result = self.whisper_model.transcribe(
            self.video_path,
            word_timestamps=True
        )
        return result

    def analyze_image(self, image_path):
        base64_image = encode_image(image_path)
        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": self.vision_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
        )
        res = response.choices[0].message.content
        return res

    def main(self):
        transcription_result = self.transcribe_video()

        # Print segments with timestamps
        with open("data.txt", "w") as w:
            for i, segment in enumerate(transcription_result["segments"]):
                start = segment["start"]
                end = segment["end"]
                text = segment["text"].strip()
                print(f"[{start:.2f} - {end:.2f}] {text}")
                w.write(f"{i}~{start:.2f}~{end:.2f}~{text}\n")
