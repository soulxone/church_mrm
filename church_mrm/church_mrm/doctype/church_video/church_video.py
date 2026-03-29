import frappe
import re
from frappe.model.document import Document


class ChurchVideo(Document):
    def validate(self):
        if self.youtube_url:
            self.video_id = self.extract_video_id(self.youtube_url)
            if not self.video_id:
                frappe.throw("Could not extract video ID from the YouTube URL. "
                             "Please use a valid YouTube link.")

    @staticmethod
    def extract_video_id(url):
        """Extract the 11-character video ID from various YouTube URL formats."""
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtube\.com/watch\?.+&v=)([a-zA-Z0-9_-]{11})',
            r'youtu\.be/([a-zA-Z0-9_-]{11})',
            r'youtube\.com/embed/([a-zA-Z0-9_-]{11})',
            r'youtube\.com/shorts/([a-zA-Z0-9_-]{11})',
            r'youtube\.com/v/([a-zA-Z0-9_-]{11})',
            r'youtube\.com/live/([a-zA-Z0-9_-]{11})',
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None
