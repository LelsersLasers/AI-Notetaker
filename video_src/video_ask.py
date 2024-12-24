from openai import OpenAI


class video_ask:
    def __init__(self, data):
        self.data = data
        self.client = OpenAI()

    def ask(self, question: str):
        assistant_id = "asst_QifpIWj4cJ4PC9WaTdHdHYnB"
        assistant = self.client.beta.assistants.retrieve(
            assistant_id=assistant_id
        )
        thread = self.client.beta.threads.create(
            messages=[{"role": "user", "content": self.data + "\n" + question}],
        )

        run = self.client.beta.threads.runs.create_and_poll(
            thread_id=thread.id,
            assistant_id=assistant.id,
        )

        if run.status == 'completed':
            messages = self.client.beta.threads.messages.list(thread_id=thread.id)
            ai_response = messages.data[0].content[0].text.value
            return ai_response
