import base64
import os
import json
import pytesseract
from pdf2image import convert_from_path
from PyPDF2 import PdfReader
from openai import OpenAI
import concurrent.futures
import threading
import shutil

# Initialize OpenAI client
assistant_id = "asst_0m9aSAgCVAVWaAnJiWwakD7s"
client = OpenAI()
vector_store = client.beta.vector_stores.create(name="Slideshows")

# Semaphore to limit concurrent API calls
api_semaphore = threading.Semaphore(5)  # Adjust based on your rate limits


def extract_text_from_pdf(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text


def extract_images_from_pdf(pdf_path):
    pages = convert_from_path(pdf_path)
    image_paths = []
    temp_dir = f"temp_images_{os.path.basename(pdf_path).replace('.pdf', '')}"
    os.makedirs(temp_dir, exist_ok=True)
    for i, page in enumerate(pages):
        image_path = os.path.join(temp_dir, f"temp_page_{i}.png")
        page.save(image_path, 'PNG')
        image_paths.append(image_path)
    return image_paths, temp_dir


def ocr_image(image_path):
    text = pytesseract.image_to_string(image_path)
    return text


def describe_image(image_path):
    def encode_image(image_path):
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')

    base64_image = encode_image(image_path)

    api_semaphore.acquire()
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Describe accurately what is in this image. Use technical terms and say what it represents. Be precise, don't talk about the context just describe what is in the image. If this image does not pertain to a computer science course (or contains a schedule, or just instructor's name, return \"Nothing useful\""

                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
        )
    finally:
        api_semaphore.release()

    data = response.choices[0].message.content
    return data


def process_image(image_path):
    image_text = ocr_image(image_path)
    image_description = describe_image(image_path)
    combined_text = f"\n\n--- Image Extracted Text ({os.path.basename(image_path)}) ---\n{image_text}\n"
    if image_description:
        combined_text += f"\n--- Image Description ({os.path.basename(image_path)}) ---\n{image_description}\n"
    return combined_text


def process_pdf(pdf_path, output_folder):
    text = extract_text_from_pdf(pdf_path)

    # Extract images
    image_paths, temp_dir = extract_images_from_pdf(pdf_path)

    # Process images in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        combined_texts = list(executor.map(process_image, image_paths))

    # Append combined texts from images
    text += ''.join(combined_texts)

    # Remove temporary image directory
    shutil.rmtree(temp_dir)

    # Save to text file
    base_name = os.path.basename(pdf_path).replace('.pdf', '.txt')
    output_path = os.path.join(output_folder, base_name)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(text)

    return output_path


def upload_processed_text(file_path):
    with open(file_path, 'rb') as f:
        client.beta.vector_stores.file_batches.upload_and_poll(
            vector_store_id=vector_store.id, files=[f]
        )


def gpt_summarize(file_name: str, slides):
    assistant = client.beta.assistants.update(
        assistant_id=assistant_id,
        tools=[{"type": "file_search"}],
        tool_resources={"file_search": {"vector_store_ids": [vector_store.id]}},
    )

    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": f"Summarize the file {file_name}",
                "attachments": [
                    {"file_id": slides.id, "tools": [{"type": "file_search"}]}
                ],
            }
        ],
    )

    run = client.beta.threads.runs.create_and_poll(
        thread_id=thread.id,
        assistant_id=assistant.id,
    )

    if run.status == 'completed':
        messages = client.beta.threads.messages.list(thread_id=thread.id)
        if len(messages.data) > 1:
            ai_response = messages.data[0].content[0].text.value
            return ai_response
        else:
            return "No response from assistant."
    else:
        return "Run did not complete successfully."


def process_and_upload_pdf(pdf_path, output_folder):
    processed_text_path = process_pdf(pdf_path, output_folder)
    upload_processed_text(processed_text_path)


def main():
    folder_path = "/Users/shay/PycharmProjects/NoteTaker/slideshows"
    output_folder = "/Users/shay/PycharmProjects/NoteTaker/processed_texts"
    os.makedirs(output_folder, exist_ok=True)

    # Collect all PDF files
    pdf_files = [f for f in os.listdir(folder_path) if f.endswith(".pdf")]
    pdf_paths = [os.path.join(folder_path, f) for f in pdf_files]

    # Process PDFs in parallel
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        for pdf_path in pdf_paths:
            print(f"Processing {os.path.basename(pdf_path)}")
            future = executor.submit(process_and_upload_pdf, pdf_path, output_folder)
            futures.append(future)

        # Wait for all PDFs to be processed
        for future in concurrent.futures.as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Exception occurred: {e}")

    vector_store_files = client.beta.vector_stores.files.list(
        vector_store_id=vector_store.id
    )

    data = {}
    with open('notes.json', 'w', encoding='utf-8') as w:
        # Summarize the files in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            summary_futures = []
            for index, file in enumerate(vector_store_files.data):
                print(f"Summarizing: {file.filename}")
                future = executor.submit(gpt_summarize, file.filename, file)
                summary_futures.append((file.filename, future))

            for file_name, future in summary_futures:
                try:
                    res = future.result()
                    print(res)
                    data[file_name] = res
                except Exception as e:
                    print(f"Exception occurred during summarization of {file_name}: {e}")

        json.dump(data, w, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    main()
