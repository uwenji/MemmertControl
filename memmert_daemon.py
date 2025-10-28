#!/usr/bin/env python3
"""
Memmert Control Daemon
Combines logger + watcher + auto-sync in one continuous process.
No crontab needed!
"""
import json
import logging
import sys
import os
import time
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

# Import from your existing atmoweb module
sys.path.insert(0, str(Path(__file__).parent / 'archive'))
from atmoweb import AtmoWebClient


class MemmertDaemon:
    """All-in-one daemon for Memmert control and monitoring."""
    
    def __init__(
        self,
        incubator_ip: str = "192.168.100.100",
        log_file: Path = Path("data/log/incubator_history.json"),
        schedule_file: Path = Path("data/schedules/setpoint_schedule.json"),
        max_hours: float = 3.0,
        log_interval: int = 60,  # seconds
        sync_interval: int = 10,  # seconds
        git_repo_path: Optional[Path] = None
    ):
        self.incubator_ip = incubator_ip
        self.log_file = log_file
        self.schedule_file = schedule_file
        self.max_hours = max_hours
        self.log_interval = log_interval
        self.sync_interval = sync_interval
        
        # Git repo path
        if git_repo_path:
            self.git_repo_path = git_repo_path
        else:
            self.git_repo_path = log_file.parent.parent.parent
        
        # Tracking files
        self.schedule_tracker = Path("data/.schedule_last_modified")
        
        # Last run times
        self.last_log_time = 0
        self.last_sync_time = 0
        
        # Setup
        self.logger = logging.getLogger(__name__)
        self._setup_git_ssh()
        
        # Create client
        self.client = AtmoWebClient(ip=incubator_ip)
    
    def _setup_git_ssh(self):
        """Setup SSH configuration for git to work in background."""
        ssh_key = None
        home = Path.home()
        
        for key_name in ['id_ed25519', 'id_rsa']:
            key_path = home / '.ssh' / key_name
            if key_path.exists():
                ssh_key = str(key_path)
                break
        
        if ssh_key:
            os.environ['GIT_SSH_COMMAND'] = f'ssh -i {ssh_key} -o IdentitiesOnly=yes -o StrictHostKeyChecking=no'
            self.logger.debug(f"Using SSH key: {ssh_key}")
    
    def git_pull(self) -> bool:
        """Pull latest changes from GitHub."""
        try:
            original_dir = Path.cwd()
            os.chdir(self.git_repo_path)
            
            try:
                # Check if there are unstaged changes
                status_result = subprocess.run(
                    ['git', 'status', '--porcelain'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                has_changes = bool(status_result.stdout.strip())
                
                # Stash if needed
                if has_changes:
                    subprocess.run(['git', 'stash'], capture_output=True, timeout=10)
                
                # Pull
                result = subprocess.run(
                    ['git', 'pull', '--rebase'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                # Pop stash if we stashed
                if has_changes:
                    subprocess.run(['git', 'stash', 'pop'], capture_output=True, timeout=10)
                
                if result.returncode == 0:
                    if "Already up to date" not in result.stdout:
                        self.logger.info("↓ Pulled updates from GitHub")
                    return True
                else:
                    self.logger.warning(f"Git pull failed: {result.stderr}")
                    return False
                    
            finally:
                os.chdir(original_dir)
                
        except Exception as e:
            self.logger.error(f"Git pull error: {e}")
            return False
    
    def git_push_with_retry(self, max_retries: int = 3, retry_delay: int = 5) -> bool:
        """
        Push to GitHub with retry logic.
        
        Args:
            max_retries: Number of retry attempts (default: 3)
            retry_delay: Seconds between retries (default: 5)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            original_dir = Path.cwd()
            os.chdir(self.git_repo_path)
            
            try:
                # Try push with retries
                for attempt in range(max_retries):
                    result = subprocess.run(
                        ['git', 'push'],
                        capture_output=True,
                        text=True,
                        timeout=30
                    )
                    
                    if result.returncode == 0:
                        self.logger.info("↑ Pushed to GitHub")
                        return True
                    
                    if attempt < max_retries - 1:
                        self.logger.warning(f"Push failed (attempt {attempt + 1}/{max_retries}), retrying in {retry_delay}s...")
                        time.sleep(retry_delay)
                
                # All retries failed, try pull + push
                self.logger.info("All retries failed, trying rebase...")
                
                # Check for unstaged changes and stash if needed
                status_result = subprocess.run(
                    ['git', 'status', '--porcelain'],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                has_changes = bool(status_result.stdout.strip())
                if has_changes:
                    subprocess.run(['git', 'stash'], capture_output=True, timeout=10)
                
                # Pull with rebase
                subprocess.run(['git', 'pull', '--rebase'], capture_output=True, timeout=30)
                
                # Pop stash if we stashed
                if has_changes:
                    subprocess.run(['git', 'stash', 'pop'], capture_output=True, timeout=10)
                
                # Try push one more time
                result = subprocess.run(
                    ['git', 'push'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    self.logger.info("↑ Pushed to GitHub (after rebase)")
                    return True
                else:
                    self.logger.error(f"Git push failed after rebase: {result.stderr}")
                    return False
                    
            finally:
                os.chdir(original_dir)
                
        except Exception as e:
            self.logger.error(f"Git push error: {e}")
            return False
    
    def git_commit_and_push(self) -> bool:
        """Commit log file and push with retry logic."""
        try:
            original_dir = Path.cwd()
            os.chdir(self.git_repo_path)
            
            try:
                # Get relative path
                log_file_rel = self.log_file.relative_to(self.git_repo_path)
                
                # Add file
                result = subprocess.run(
                    ['git', 'add', str(log_file_rel)],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode != 0:
                    self.logger.error(f"Git add failed: {result.stderr}")
                    return False
                
                # Check if changes exist
                status_result = subprocess.run(
                    ['git', 'status', '--porcelain', str(log_file_rel)],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if not status_result.stdout.strip():
                    return True  # No changes
                
                # Commit
                commit_msg = f"Update log: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                result = subprocess.run(
                    ['git', 'commit', '-m', commit_msg],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode != 0:
                    self.logger.error(f"Git commit failed: {result.stderr}")
                    return False
                
                # Push with retry
                return self.git_push_with_retry(max_retries=3, retry_delay=5)
                
            finally:
                os.chdir(original_dir)
                
        except Exception as e:
            self.logger.error(f"Git operation error: {e}")
            return False
    
    def read_incubator_data(self) -> Dict[str, Any]:
        """Read current data from incubator."""
        timestamp = datetime.now().isoformat()
        
        try:
            readings = self.client.get_readings()
            setpoints = self.client.get_setpoints()
            
            try:
                mode_response = self.client.query(CurOp="")
                current_mode = mode_response.get('CurOp', 'Unknown')
            except:
                current_mode = 'Unknown'
            
            entry = {
                'timestamp': timestamp,
                'mode': current_mode,
                'readings': readings,
                'setpoints': setpoints
            }
            
            self.logger.info(f"📊 Temp={readings.get('Temp1Read', 'N/A')}°C, Hum={readings.get('HumRead', 'N/A')}%")
            return entry
            
        except Exception as e:
            self.logger.error(f"Failed to read incubator: {e}")
            return {
                'timestamp': timestamp,
                'error': str(e),
                'readings': {},
                'setpoints': {}
            }
    
    def load_history(self) -> Dict[str, Any]:
        """Load existing history."""
        if not self.log_file.exists():
            return {
                'metadata': {
                    'created': datetime.now().isoformat(),
                    'device_ip': self.incubator_ip,
                    'max_hours': self.max_hours,
                    'description': 'Rolling history of Memmert incubator data'
                },
                'data': []
            }
        
        try:
            with open(self.log_file, 'r') as f:
                return json.load(f)
        except:
            return {
                'metadata': {
                    'created': datetime.now().isoformat(),
                    'device_ip': self.incubator_ip,
                    'max_hours': self.max_hours
                },
                'data': []
            }
    
    def trim_old_data(self, data: list) -> list:
        """Remove data older than max_hours."""
        if not data:
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=self.max_hours)
        
        trimmed_data = []
        for entry in data:
            try:
                entry_time = datetime.fromisoformat(entry['timestamp'])
                if entry_time >= cutoff_time:
                    trimmed_data.append(entry)
            except:
                continue
        
        removed = len(data) - len(trimmed_data)
        if removed > 0:
            self.logger.info(f"🗑️  Trimmed {removed} old entries")
        
        return trimmed_data
    
    def save_history(self, history: Dict[str, Any]):
        """Save history to file."""
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        history['metadata']['last_updated'] = datetime.now().isoformat()
        history['metadata']['total_entries'] = len(history.get('data', []))
        
        if history['data']:
            first_time = datetime.fromisoformat(history['data'][0]['timestamp'])
            last_time = datetime.fromisoformat(history['data'][-1]['timestamp'])
            time_span = (last_time - first_time).total_seconds() / 3600
            history['metadata']['time_span_hours'] = round(time_span, 2)
        
        with open(self.log_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def log_data(self):
        """Log current incubator data."""
        try:
            current_data = self.read_incubator_data()
            history = self.load_history()
            history['data'].append(current_data)
            history['data'] = self.trim_old_data(history['data'])
            self.save_history(history)
            
            # Commit and push
            self.git_commit_and_push()
            
            self.last_log_time = time.time()
            
        except Exception as e:
            self.logger.error(f"Logging failed: {e}", exc_info=True)
    
    def check_schedule_update(self):
        """Check if schedule file changed and run scheduler if needed."""
        if not self.schedule_file.exists():
            return
        
        current_mtime = os.path.getmtime(self.schedule_file)
        
        # Load last known time
        last_mtime = None
        if self.schedule_tracker.exists():
            try:
                with open(self.schedule_tracker, 'r') as f:
                    last_mtime = float(f.read().strip())
            except:
                pass
        
        # Check if changed
        if last_mtime is None or current_mtime > last_mtime:
            self.logger.info("📅 Schedule updated! Running scheduler...")
            
            try:
                result = subprocess.run(
                    [sys.executable, 'memmert_scheduler.py',
                     '--schedule', str(self.schedule_file),
                     '--ip', self.incubator_ip,
                     '--once'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode == 0:
                    self.logger.info("✓ Scheduler executed")
                else:
                    self.logger.error(f"Scheduler failed: {result.stderr}")
                    
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
            
            # Save new modification time
            self.schedule_tracker.parent.mkdir(parents=True, exist_ok=True)
            with open(self.schedule_tracker, 'w') as f:
                f.write(str(current_mtime))
    
    def sync_check(self):
        """Check for GitHub updates every sync_interval."""
        current_time = time.time()
        
        if current_time - self.last_sync_time >= self.sync_interval:
            self.git_pull()
            self.check_schedule_update()
            self.last_sync_time = current_time
    
    def run(self):
        """Main daemon loop."""
        self.logger.info("🚀 Memmert Daemon started")
        self.logger.info(f"   Log interval: {self.log_interval}s")
        self.logger.info(f"   Sync interval: {self.sync_interval}s")
        self.logger.info(f"   Incubator: {self.incubator_ip}")
        self.logger.info("")
        
        try:
            while True:
                current_time = time.time()
                
                # Log data every log_interval
                if current_time - self.last_log_time >= self.log_interval:
                    self.log_data()
                
                # Sync check every sync_interval
                self.sync_check()
                
                # Sleep for 1 second to avoid busy loop
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("\n🛑 Daemon stopped")
        except Exception as e:
            self.logger.error(f"Daemon error: {e}", exc_info=True)


def main():
    """Entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Memmert Control Daemon')
    parser.add_argument('--ip', default='192.168.100.100', help='Incubator IP')
    parser.add_argument('--log-interval', type=int, default=60, help='Logging interval (seconds)')
    parser.add_argument('--sync-interval', type=int, default=10, help='GitHub sync interval (seconds)')
    parser.add_argument('--max-hours', type=float, default=3.0, help='Max hours of data to keep')
    parser.add_argument('--verbose', action='store_true', help='Verbose logging')
    
    args = parser.parse_args()
    
    # Setup logging
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Create and run daemon
    daemon = MemmertDaemon(
        incubator_ip=args.ip,
        log_interval=args.log_interval,
        sync_interval=args.sync_interval,
        max_hours=args.max_hours
    )
    
    daemon.run()


if __name__ == '__main__':
    main()