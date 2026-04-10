import uuid, datetime

class AIService:
    def __init__(self):
        pass

    def generate(self, org_id: str, channel_id: str, user_id: str, payload):
        job_id = str(uuid.uuid4())
        output_url = f"https://storage.local/ai/{job_id}.txt"
        return {
            "job_id": job_id,
            "status": "succeeded",
            "output_url": output_url,
            "model_used": "gemini-2.5-pro"
        }

    def history(self, org_id: str, task_id: str):
        now = datetime.datetime.utcnow().isoformat() + "Z"
        return [{
            "id": str(uuid.uuid4()),
            "persona": "max",
            "mode": "script",
            "model_used": "gemini-2.5-pro",
            "output_url": "https://storage.local/ai/sample.txt",
            "created_at": now,
            "status": "succeeded",
            "prompt_preview": "Intro about the race..."
        }]

