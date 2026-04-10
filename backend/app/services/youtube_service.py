class YouTubeService:
    def fetch_daily_summary(self, org_id: str, channel_id: str):
        return [
            {"date":"2025-10-25","views":1200,"watch_time":800},
            {"date":"2025-10-26","views":1500,"watch_time":950},
            {"date":"2025-10-27","views":1800,"watch_time":1020},
            {"date":"2025-10-28","views":1600,"watch_time":970},
            {"date":"2025-10-29","views":2100,"watch_time":1200},
            {"date":"2025-10-30","views":2400,"watch_time":1300},
            {"date":"2025-10-31","views":2300,"watch_time":1280}
        ]

    def fetch_top_videos(self, org_id: str, channel_id: str):
        return [
            {"title":"Race Recap","ctr":6.1},
            {"title":"Pit Stop Secrets","ctr":5.4},
            {"title":"Setup Myths","ctr":4.9},
            {"title":"Quali Drama","ctr":4.7},
            {"title":"Undercut 101","ctr":4.6}
        ]
