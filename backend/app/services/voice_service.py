import uuid

class VoiceService:
    def __init__(self):
        pass

    def generate(self, org_id: str, channel_id: str, user_id: str, text: str, voice_id: str | None):
        job_id = str(uuid.uuid4())
        return {"job_id": job_id, "status": "queued"}

    def status(self, job_id: str):
        return {"job_id": job_id, "status": "succeeded", "output_url": f"https://storage.local/voice/{job_id}.mp3"}

