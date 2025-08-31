import time
import threading
import schedule
from datetime import datetime, time as dt_time
from typing import Callable, Optional
import logging

class Scheduler:
    def __init__(self, interval_minutes: int = 10):
        self.interval_minutes = interval_minutes
        self.callback = None
        self.thread = None
        self.running = False
        self.schedule_jobs = []
        self.logger = logging.getLogger(__name__)

    def start(self, callback: Callable):
        """Start the scheduler with a callback function"""
        self.callback = callback
        self.running = True

        if self.interval_minutes > 0:
            # Traditional interval-based scheduling
            self.thread = threading.Thread(target=self._run_interval)
            self.thread.daemon = True
            self.thread.start()
        else:
            # Time-based scheduling
            self._setup_time_based_schedule()

    def stop(self):
        """Stop the scheduler"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=1)

        # Clear all scheduled jobs
        schedule.clear()
        self.schedule_jobs = []

    def _run_interval(self):
        """Run interval-based scheduling"""
        while self.running:
            time.sleep(self.interval_minutes * 60)
            if self.running and self.callback:
                try:
                    self.callback()
                except Exception as e:
                    self.logger.error(f"Scheduler callback error: {e}")

    def _setup_time_based_schedule(self):
        """Setup time-based scheduling using schedule library"""
        # This would be configured through config
        pass

    def schedule_at_time(self, time_str: str, callback: Callable):
        """Schedule a callback at a specific time (HH:MM format)"""
        try:
            hour, minute = map(int, time_str.split(':'))
            schedule.every().day.at(time_str).do(callback)
            self.schedule_jobs.append(f"daily at {time_str}")
            self.logger.info(f"Scheduled daily commit at {time_str}")
        except ValueError as e:
            self.logger.error(f"Invalid time format: {time_str}. Use HH:MM")

    def schedule_weekly(self, day: str, time_str: str, callback: Callable):
        """Schedule a callback on a specific day and time"""
        days_map = {
            'monday': schedule.every().monday,
            'tuesday': schedule.every().tuesday,
            'wednesday': schedule.every().wednesday,
            'thursday': schedule.every().thursday,
            'friday': schedule.every().friday,
            'saturday': schedule.every().saturday,
            'sunday': schedule.every().sunday
        }

        if day.lower() not in days_map:
            self.logger.error(f"Invalid day: {day}")
            return

        try:
            days_map[day.lower()].at(time_str).do(callback)
            self.schedule_jobs.append(f"{day} at {time_str}")
            self.logger.info(f"Scheduled weekly commit on {day} at {time_str}")
        except Exception as e:
            self.logger.error(f"Failed to schedule weekly: {e}")

    def schedule_hourly(self, minute: int, callback: Callable):
        """Schedule a callback every hour at a specific minute"""
        if not 0 <= minute <= 59:
            self.logger.error("Minute must be between 0 and 59")
            return

        schedule.every().hour.at(f":{minute:02d}").do(callback)
        self.schedule_jobs.append(f"hourly at minute {minute}")
        self.logger.info(f"Scheduled hourly commit at minute {minute}")

    def pause_scheduling(self):
        """Pause all scheduled jobs"""
        # This would require more complex state management
        self.logger.info("Scheduling paused")

    def resume_scheduling(self):
        """Resume all scheduled jobs"""
        # This would require more complex state management
        self.logger.info("Scheduling resumed")

    def get_scheduled_jobs(self) -> list:
        """Get list of currently scheduled jobs"""
        return self.schedule_jobs.copy()

    def clear_schedule(self):
        """Clear all scheduled jobs"""
        schedule.clear()
        self.schedule_jobs = []
        self.logger.info("All scheduled jobs cleared")

    def run_pending(self):
        """Run any pending scheduled jobs (for time-based scheduling)"""
        schedule.run_pending()
