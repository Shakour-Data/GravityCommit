import time
import threading
from typing import Callable, Optional
import schedule

class Scheduler:
    def __init__(self, interval_minutes: int = 10):
        self.interval = interval_minutes
        self.job = None
        self.running = False
        self.thread = None
        self.callback = None

    def start(self, callback: Callable):
        """Start the scheduler with given callback function"""
        if self.running:
            return

        self.callback = callback
        self.running = True

        # Schedule the job
        self.job = schedule.every(self.interval).minutes.do(self._run_callback)

        # Start the scheduler in a separate thread
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()

    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.job:
            schedule.cancel_job(self.job)
            self.job = None
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)

    def set_interval(self, interval_minutes: int):
        """Update the scheduling interval"""
        old_running = self.running
        if old_running:
            self.stop()

        self.interval = interval_minutes

        if old_running:
            self.start(self.callback)

    def _run_scheduler(self):
        """Run the scheduler loop"""
        while self.running:
            schedule.run_pending()
            time.sleep(1)

    def _run_callback(self):
        """Execute the callback function"""
        if self.callback:
            try:
                self.callback()
            except Exception as e:
                print(f"Scheduler callback error: {e}")
