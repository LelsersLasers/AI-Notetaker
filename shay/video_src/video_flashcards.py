from openai import OpenAI


class video_flashcards:
    def __init__(self, data_path):
        self.client = OpenAI()
        with open(data_path, 'r') as f:
            self.data = "\n".join(f.readlines())
        print(self.data)

    def create_flashcards(self) -> str:
        assistant_id = "asst_zrMwZED8JIfVavM6VEv2r5To"
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

    def main(self):
        flashcards = self.create_flashcards().split('\n')
        parsed_flashcards = []
        print(flashcards)
        for f in flashcards:
            if len(f.split('~~~')) != 2:
                print(len(f.split('~~~')))
                continue
            parsed_flashcards.append({
                "question": f.split('~~~')[0],
                "answer": f.split('~~~')[1]
            })
        print('Parsed flashcards: ' + str(parsed_flashcards))
        return parsed_flashcards
