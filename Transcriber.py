# Transcribes a slideshow into text notes
from openai import OpenAI

def create_assistant_and_ask(model, data):
    client = OpenAI()
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": data}
        ]
    )
    print(completion.choices[0].message.content)