from openai import OpenAI


class video_notes:
    def __init__(self, data_path):
        self.client = OpenAI()
        with open(data_path, 'r') as f:
            self.data = "\n".join(f.readlines())
        print(self.data)

    def create_notes(self) -> str:
        assistant_id = "asst_LAvhUmMCgVxQ6FX1ZhDBCTUx"
        assistant = self.client.beta.assistants.retrieve(
            assistant_id=assistant_id
        )
        thread = self.client.beta.threads.create(
            messages=[{"role": "user", "content": self.data}]
        )

        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )

        if run.status == 'completed':
            messages = self.client.beta.threads.messages.list(thread_id=thread.id)
            ai_response = messages.data[0].content[0].text.value
            return ai_response

    def describe_image(self, image_path):
        pass

    def main(self):
        notes = self.create_notes()
        return notes
