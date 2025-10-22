#!/usr/bin/env python3
"""
Memmert Incubator Scheduler
Executes setpoint schedules from JSON files to control Memmert incubators via AtmoWEB.
"""
import json
import logging
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse

from archive.atmoweb import AtmoWebClient


class ScheduleExecutor:
    """Executes setpoint schedules for Memmert incubators."""
    
    def __init__(self, client: AtmoWebClient, schedule_file: Path, 
                 check_interval: int = 30, tolerance: int = 60):
        """
        Initialize the schedule executor.
        
        Args:
            client: AtmoWebClient instance for device communication
            schedule_file: Path to the schedule JSON file
            check_interval: How often to check for scheduled changes (seconds)
            tolerance: Time window for executing scheduled changes (seconds)
        """
        self.client = client
        self.schedule_file = schedule_file
        self.check_interval = check_interval
        self.tolerance = tolerance
        self.schedule = None
        self.executed_points = set()
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
    
    def load_schedule(self) -> Dict[str, Any]:
        """
        Load and validate the schedule file.
        
        Returns:
            Parsed schedule dictionary
            
        Raises:
            FileNotFoundError: If schedule file doesn't exist
            json.JSONDecodeError: If schedule file is invalid JSON
            ValueError: If schedule structure is invalid
        """
        if not self.schedule_file.exists():
            raise FileNotFoundError(f"Schedule file not found: {self.schedule_file}")
        
        with open(self.schedule_file, 'r') as f:
            schedule = json.load(f)
        
        # Validate schedule structure
        if 'schedule' not in schedule:
            raise ValueError("Schedule file must contain 'schedule' key")
        
        if not isinstance(schedule['schedule'], list):
            raise ValueError("'schedule' must be a list of setpoint entries")
        
        self.schedule = schedule
        self.logger.info(f"Loaded schedule with {len(schedule['schedule'])} setpoints")
        return schedule
    
    def parse_timestamp(self, timestamp_str: str) -> datetime:
        """
        Parse ISO 8601 timestamp string.
        
        Args:
            timestamp_str: ISO format timestamp string
            
        Returns:
            datetime object
        """
        # Handle both with and without timezone info
        if timestamp_str.endswith('Z'):
            timestamp_str = timestamp_str[:-1] + '+00:00'
        
        return datetime.fromisoformat(timestamp_str)
    
    def apply_setpoints(self, setpoints: Dict[str, float]) -> Dict[str, Any]:
        """
        Apply setpoints to the incubator.
        
        Args:
            setpoints: Dictionary of parameter keys to values
            
        Returns:
            Dictionary of applied values and any errors
        """
        results = {
            'success': [],
            'failed': [],
            'not_available': []
        }
        
        for key, value in setpoints.items():
            try:
                actual_value = self.client.set_parameter(key, value)
                results['success'].append({
                    'parameter': key,
                    'requested': value,
                    'actual': actual_value
                })
                self.logger.info(f"✓ Set {key}={value} (actual: {actual_value})")
                
            except ValueError as e:
                # Value out of range
                results['failed'].append({
                    'parameter': key,
                    'value': value,
                    'error': str(e)
                })
                self.logger.error(f"✗ Failed to set {key}={value}: {e}")
                
            except KeyError as e:
                # Parameter not available on this device
                results['not_available'].append({
                    'parameter': key,
                    'value': value,
                    'error': str(e)
                })
                self.logger.warning(f"⚠ Parameter {key} not available on device")
                
            except Exception as e:
                # Other errors
                results['failed'].append({
                    'parameter': key,
                    'value': value,
                    'error': str(e)
                })
                self.logger.error(f"✗ Unexpected error setting {key}={value}: {e}")
        
        return results
    
    def check_and_execute(self, now: Optional[datetime] = None) -> bool:
        """
        Check if any scheduled setpoints should be executed now.
        
        Args:
            now: Current time (defaults to datetime.now())
            
        Returns:
            True if any setpoints were executed
        """
        if now is None:
            now = datetime.now()
        
        if self.schedule is None:
            self.logger.error("No schedule loaded")
            return False
        
        executed = False
        
        for idx, entry in enumerate(self.schedule['schedule']):
            # Skip if already executed
            point_id = f"{entry['timestamp']}_{idx}"
            if point_id in self.executed_points:
                continue
            
            scheduled_time = self.parse_timestamp(entry['timestamp'])
            
            # Make both timezone-aware or both naive for comparison
            if scheduled_time.tzinfo is None:
                scheduled_time = scheduled_time.replace(tzinfo=None)
                now_compare = now.replace(tzinfo=None)
            else:
                now_compare = now
                if now_compare.tzinfo is None:
                    # Assume UTC if no timezone
                    from datetime import timezone
                    now_compare = now_compare.replace(tzinfo=timezone.utc)
            
            # Check if within execution window
            time_diff = (now_compare - scheduled_time).total_seconds()
            
            if -self.tolerance <= time_diff <= self.tolerance:
                self.logger.info(f"\n{'='*60}")
                self.logger.info(f"Executing scheduled setpoints at {scheduled_time}")
                self.logger.info(f"Current time: {now_compare}")
                self.logger.info(f"{'='*60}")
                
                setpoints = entry.get('setpoints', {})
                results = self.apply_setpoints(setpoints)
                
                # Mark as executed
                self.executed_points.add(point_id)
                executed = True
                
                # Log summary
                self.logger.info(f"\nExecution summary:")
                self.logger.info(f"  Success: {len(results['success'])}")
                self.logger.info(f"  Failed: {len(results['failed'])}")
                self.logger.info(f"  Not available: {len(results['not_available'])}")
        
        return executed
    
    def get_next_scheduled_time(self, now: Optional[datetime] = None) -> Optional[datetime]:
        """
        Get the next scheduled setpoint time.
        
        Args:
            now: Current time (defaults to datetime.now())
            
        Returns:
            Next scheduled datetime, or None if no future schedules
        """
        if now is None:
            now = datetime.now()
        
        if self.schedule is None:
            return None
        
        future_times = []
        
        for idx, entry in enumerate(self.schedule['schedule']):
            point_id = f"{entry['timestamp']}_{idx}"
            if point_id in self.executed_points:
                continue
            
            scheduled_time = self.parse_timestamp(entry['timestamp'])
            
            # Make timezone-aware comparison
            if scheduled_time.tzinfo is None:
                scheduled_time = scheduled_time.replace(tzinfo=None)
                now_compare = now.replace(tzinfo=None)
            else:
                now_compare = now
                if now_compare.tzinfo is None:
                    from datetime import timezone
                    now_compare = now_compare.replace(tzinfo=timezone.utc)
            
            if scheduled_time > now_compare:
                future_times.append(scheduled_time)
        
        return min(future_times) if future_times else None
    
    def run_continuous(self, duration_hours: Optional[float] = None):
        """
        Run the scheduler continuously.
        
        Args:
            duration_hours: Run for specified hours (None = run indefinitely)
        """
        start_time = datetime.now()
        
        self.logger.info("Starting scheduler...")
        self.logger.info(f"Check interval: {self.check_interval} seconds")
        self.logger.info(f"Time tolerance: {self.tolerance} seconds")
        
        if duration_hours:
            self.logger.info(f"Will run for {duration_hours} hours")
            end_time = start_time + timedelta(hours=duration_hours)
        else:
            self.logger.info("Running indefinitely (Ctrl+C to stop)")
            end_time = None
        
        try:
            while True:
                now = datetime.now()
                
                # Check if we should stop
                if end_time and now >= end_time:
                    self.logger.info("Scheduled duration completed")
                    break
                
                # Execute any due setpoints
                self.check_and_execute(now)
                
                # Show next scheduled time
                next_time = self.get_next_scheduled_time(now)
                if next_time:
                    time_until = (next_time - now).total_seconds()
                    self.logger.debug(
                        f"Next scheduled change in {time_until:.0f} seconds "
                        f"at {next_time.strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                else:
                    self.logger.info("No more scheduled setpoints")
                    break
                
                # Sleep until next check
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            self.logger.info("\nScheduler stopped by user")
        except Exception as e:
            self.logger.error(f"Scheduler error: {e}", exc_info=True)
            raise
    
    def run_once(self):
        """Execute any currently due setpoints and exit."""
        self.logger.info("Running single check...")
        executed = self.check_and_execute()
        
        if not executed:
            next_time = self.get_next_scheduled_time()
            if next_time:
                now = datetime.now()
                time_until = (next_time - now).total_seconds()
                self.logger.info(
                    f"No setpoints due now. Next change in {time_until:.0f} seconds "
                    f"at {next_time.strftime('%Y-%m-%d %H:%M:%S')}"
                )
            else:
                self.logger.info("No scheduled setpoints found")


def setup_logging(verbose: bool = False):
    """Configure logging."""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Execute setpoint schedules for Memmert incubators'
    )
    parser.add_argument(
        '--ip',
        default='192.168.100.100',
        help='IP address of the Memmert device (default: 192.168.100.100)'
    )
    parser.add_argument(
        '--schedule',
        type=Path,
        default=Path('data/schedules/setpoint_schedule_2025-09-11T08-35-12.json'),
        help='Path to schedule JSON file'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run once and exit (useful for cron jobs)'
    )
    parser.add_argument(
        '--duration',
        type=float,
        help='Run for specified hours (default: run until schedule complete)'
    )
    parser.add_argument(
        '--check-interval',
        type=int,
        default=30,
        help='How often to check for scheduled changes in seconds (default: 30)'
    )
    parser.add_argument(
        '--tolerance',
        type=int,
        default=60,
        help='Time window for executing scheduled changes in seconds (default: 60)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable debug logging'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # Create AtmoWeb client
    try:
        client = AtmoWebClient(ip=args.ip)
        logger.info(f"Connected to Memmert device at {args.ip}")
        
        # Test connection
        status = client.get_setpoints()
        logger.info(f"Current setpoints: {status}")
        
    except Exception as e:
        logger.error(f"Failed to connect to device: {e}")
        return 1
    
    # Create and run scheduler
    try:
        executor = ScheduleExecutor(
            client=client,
            schedule_file=args.schedule,
            check_interval=args.check_interval,
            tolerance=args.tolerance
        )
        
        # Load schedule
        executor.load_schedule()
        
        # Run scheduler
        if args.once:
            executor.run_once()
        else:
            executor.run_continuous(duration_hours=args.duration)
        
        return 0
        
    except FileNotFoundError as e:
        logger.error(str(e))
        return 1
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in schedule file: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    exit(main())
