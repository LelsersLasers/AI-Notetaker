# Transcribes a slideshow into text notes
import os

from openai import OpenAI
from flask import Flask, request
from flask_cors import CORS

prompt = ("You are a student with expert notetaking skills. You will receive transcriptions of slides and will take "
          "careful and useful notes. Especially focus on small details in your answer. You are taking notes on the presentation, not talking about the presentation. Write notes that will be used to study for an exam. Do not speak to the user, rather just write effective notes to understand the material. Do not summarize your answer at the end or have an introduction to what you will do, simply do it. Focus on understanding rather than memorizing. Only write about course content, other things such as schedule, professor info, etc. are not relevant.Here are the slides \n")

prompt2 = ("You are a student with expert notetaking skills. You will receive transcriptions of slides and will make "
           "flash cards. They will be used to study for an upcoming exam on the content. Make the cards concise, "
           "and try to make the front be one word and the back be a simple definition. yet cover small details in the "
           "slides. Don't create flash cards about example problems, only new material in the lecture. Don't write "
           "cards for anything not related to course content such as schedules, test taking tips, labs, etc. Try to "
           "have the front of the card be the term, and the back be a definition or explination. Seperate the cards "
           "front~~~back with the \"~~~\" characters between them. Only return these cards and nothing else. Write "
           "1-5 note cards for the slides. Here are the slides: \n")

app = Flask('AI Slides Notetaker')
CORS(app)

def create_assistant_and_ask(model, data):
    client = OpenAI()
    completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt2 + data}
        ]
    )
    res = completion.choices[0].message.content
    print(res)
    return res


def main():
    folder_path = "/Users/shay/PycharmProjects/NoteTaker/processed_texts"
    output_file = "notes.txt"
    files = [f for f in os.listdir(folder_path)]
    notes = ""
    # os.chmod(output_file)
    with open(output_file, 'w') as w:
        for file in files:
            with open(os.path.join(folder_path, file), 'r') as f:
                lines = f.readlines()
                res = create_assistant_and_ask('gpt-4o', ''.join(lines))
                w.writelines(res.split('\n'))
                notes += res
    return notes




# You are going to be given flash cards and you will sanitize them. Remove all cards that are irrelevant to course content (such as schedule, club info, etc.). Remove all cards that are overlapping with another card. Remove cards that seem excessively simple. Rewrite cards that are needed to be better and more accurate. Ensure all information you put is extremely accurate. Remove cards that are overly easy or simple. Simplify cards if needed to be better. Keep the card formatting but remove any other formatting that is not needed. Fix gramatical/spelling mistakes.
