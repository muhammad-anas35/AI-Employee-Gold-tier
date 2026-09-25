"""Social Media Scheduler - Queue and schedule posts"""
import json
import time
import schedule
import threading
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict

from nexus.config import LOGS, PENDING_APPROVAL, APPROVED

@dataclass
class ScheduledPost:
    id: str
    platform: str
    content: str
    image_path: Optional[str]
    scheduled_for: str
    created_at: str
    status: str = "scheduled"

class SocialScheduler:
    """Manages scheduled social media posts"""
    
    def __init__(self):
        self.queue_file = LOGS.parent / "social_queue.json"
        self.posts: List[ScheduledPost] = []
        self.running = False
        self._load_queue()
    
    def _load_queue(self):
        """Load scheduled posts from file"""
        if self.queue_file.exists():
            try:
                with open(self.queue_file, 'r') as f:
                    data = json.load(f)
                    self.posts = [ScheduledPost(**p) for p in data]
            except Exception:
                self.posts = []
    
    def _save_queue(self):
        """Save scheduled posts to file"""
        with open(self.queue_file, 'w') as f:
            json.dump([asdict(p) for p in self.posts], f, indent=2)
    
    def schedule_post(self, platform: str, content: str, scheduled_for: str, image_path: str = None) -> str:
        """Schedule a post for later"""
        post_id = f"{platform}_{int(time.time())}"
        post = ScheduledPost(
            id=post_id,
            platform=platform,
            content=content,
            image_path=image_path,
            scheduled_for=scheduled_for,
            created_at=datetime.now().isoformat()
        )
        self.posts.append(post)
        self._save_queue()
        return post_id
    
    def get_due_posts(self) -> List[ScheduledPost]:
        """Get posts that are due for publishing"""
        now = datetime.now()
        due = []
        for post in self.posts:
            if post.status == "scheduled":
                scheduled = datetime.fromisoformat(post.scheduled_for)
                if scheduled <= now:
                    due.append(post)
        return due
    
    def mark_published(self, post_id: str):
        """Mark a post as published"""
        for post in self.posts:
            if post.id == post_id:
                post.status = "published"
                self._save_queue()
                break
    
    def mark_failed(self, post_id: str, error: str):
        """Mark a post as failed"""
        for post in self.posts:
            if post.id == post_id:
                post.status = "failed"
                post.error = error
                self._save_queue()
                break
    
    def cancel_post(self, post_id: str):
        """Cancel a scheduled post"""
        self.posts = [p for p in self.posts if p.id != post_id]
        self._save_queue()
    
    def list_scheduled(self) -> List[ScheduledPost]:
        """List all scheduled posts"""
        return [p for p in self.posts if p.status == "scheduled"]
    
    def start_scheduler(self):
        """Start the background scheduler"""
        self.running = True
        def run():
            while self.running:
                due_posts = self.get_due_posts()
                for post in due_posts:
                    print(f"Publishing scheduled post: {post.id}")
                    # This would call the actual publishing functions
                    # For now, just mark as published
                    self.mark_published(post.id)
                time.sleep(60)  # Check every minute
        
        self.thread = threading.Thread(target=run, daemon=True)
        self.thread.start()
    
    def stop_scheduler(self):
        """Stop the background scheduler"""
        self.running = False
