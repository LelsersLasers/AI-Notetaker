import json
import os

from flask import Flask, request, jsonify
from flask_cors import CORS
from slides_src import transcriber
from slides_src.notetaker import notetaker
from video_src.video_ask import video_ask
from video_src.video_analyzer import video_analyzer
from video_src.video_flashcards import video_flashcards
from video_src.video_notes import video_notes
from video_src.video_screenshots import video_screenshots

app = Flask('Finals Helper')
CORS(app)


def sanitize(filename: str):
    filename = filename.replace(' ', '')
    if filename.count('/') > 0:
        filename = filename.split('/')[-1]
    return filename


@app.route("/slides", methods=['POST'])
def slides():
    uploaded_files = request.files.getlist('slidesFolder[]')
    folder_path = 'slideshows'
    if not uploaded_files:
        return jsonify({
            "success": False,
            "message": "No slides uploaded."
        })
    if not os.path.exists(folder_path):
        print('Path does not exist')
    for f in uploaded_files:
        f.filename = sanitize(f.filename)
        f.save(os.path.join(folder_path, sanitize(f.filename)))
    # n = notetaker().main(folder_path)
    return json.dumps({"success": True, "flashcards": transcriber.main()})


@app.route("/video_flashcards", methods=['POST'])
def video_flashcards_creator():
    video_obj = request.files.get('videoFile')
    video_path = 'video_src/' + sanitize(video_obj.filename)
    video_obj.save(video_path)
    # video_screenshots(video_path, 50).main()
    # video_analyzer(video_path, 'video_src/video_screenshots').main()
    return jsonify({
        'success': True,
        'flashcards': video_flashcards('data.txt').main()})


@app.route("/video_notes", methods=['POST'])
def post_video_notes():
    video_obj = request.files.get('videoFile')
    video_path = 'video_src/' + sanitize(video_obj.filename)
    # video_obj.save(video_path)
    # video_screenshots(video_path, 50).main()
    # video_analyzer(video_path, 'video_src/video_screenshots').main()
    return jsonify({
        'success': True,
        'notes': video_notes('data.txt').main(),
    })


@app.route("/video_ask", methods=['POST'])
def video_ask_question():
    question = request.json['question']
    with open('video_src/data.txt', 'r') as f:
        data = "\n".join(f.readlines())
    ask_obj = video_ask(data)
    return jsonify({
        'success': True,
        'answer': ask_obj.ask(question)
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
