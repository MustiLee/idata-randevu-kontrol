import logging
import signal
import sys
import threading
from datetime import datetime
from typing import Callable, Optional

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

logger = logging.getLogger(__name__)


class AppointmentScheduler:
    """Manages scheduled appointment checks."""
    
    def __init__(self, check_interval_minutes: int = 10):
        self.check_interval_minutes = check_interval_minutes
        self.scheduler = BlockingScheduler()
        self.is_running = False
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)
    
    def start(self, check_function: Callable, initial_check: bool = True):
        """
        Start the scheduler.
        
        Args:
            check_function: Function to call for checking appointments
            initial_check: Whether to run an initial check immediately
        """
        if self.is_running:
            logger.warning("Scheduler is already running")
            return
        
        logger.info(f"Starting scheduler with {self.check_interval_minutes} minute interval")
        
        # Run initial check if requested
        if initial_check:
            logger.info("Running initial appointment check...")
            self._run_check(check_function)
        
        # Schedule recurring checks
        self.scheduler.add_job(
            func=lambda: self._run_check(check_function),
            trigger=IntervalTrigger(minutes=self.check_interval_minutes),
            id='appointment_check',
            name='Check Italy visa appointments',
            misfire_grace_time=60  # Allow 60 seconds grace time for missed jobs
        )
        
        # Start scheduler
        self.is_running = True
        try:
            logger.info("Scheduler started. Press Ctrl+C to stop.")
            self.scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            logger.info("Scheduler stopped by user")
        finally:
            self.is_running = False
    
    def stop(self):
        """Stop the scheduler."""
        if self.scheduler.running:
            self.scheduler.shutdown()
            self.is_running = False
            logger.info("Scheduler stopped")
    
    def _run_check(self, check_function: Callable):
        """
        Run the appointment check function.
        
        Args:
            check_function: Function to call for checking appointments
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logger.info(f"[{timestamp}] Starting appointment check...")
            
            # Run the check function
            check_function()
            
            logger.info(f"[{timestamp}] Appointment check completed")
            
        except Exception as e:
            logger.error(f"Error during appointment check: {e}", exc_info=True)
    
    def add_job(self, func: Callable, trigger, **kwargs):
        """
        Add a custom job to the scheduler.
        
        Args:
            func: Function to schedule
            trigger: APScheduler trigger
            **kwargs: Additional job parameters
        """
        return self.scheduler.add_job(func, trigger, **kwargs)
    
    def remove_job(self, job_id: str):
        """
        Remove a job from the scheduler.
        
        Args:
            job_id: ID of the job to remove
        """
        self.scheduler.remove_job(job_id)
    
    def get_jobs(self):
        """Get all scheduled jobs."""
        return self.scheduler.get_jobs()
    
    def print_jobs(self):
        """Print information about all scheduled jobs."""
        jobs = self.get_jobs()
        if not jobs:
            logger.info("No scheduled jobs")
            return
        
        logger.info(f"Scheduled jobs ({len(jobs)}):")
        for job in jobs:
            logger.info(f"  - {job.name} (ID: {job.id})")
            logger.info(f"    Next run: {job.next_run_time}")
            logger.info(f"    Trigger: {job.trigger}")