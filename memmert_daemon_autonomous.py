#!/usr/bin/env python3
"""
Memmert Control Daemon - Fully Autonomous
Handles all git conflicts automatically, no manual intervention needed.
"""
import json
import logging
import sys
import os
import time
import subprocess
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

# Import from your existing atmoweb module
sys.path.insert(0, str(Path(__file__).parent / 'archive'))
from atmoweb import AtmoWebClient


class MemmertDaemon:
    """Fully autonomous daemon with smart git conflict resolution."""
    
    def __init__(
        self,
        incubator_ip: str = "192.168.100.100",
        log_file: Path = Path("data/log/incubator_history.json"),
        schedule_file: Path = Path("data/schedules/setpoint_schedule.json"),
        max_hours: float = 3.0,
        log_interval: int = 60,
        sync_interval: int = 10,
        git_repo_path: Optional[Path] = None
    ):
        self.incubator_ip = incubator_ip
        self.log_file = log_file
        self.schedule_file = schedule_file
        self.max_hours = max_hours
        self.log_interval = log_interval
        self.sync_interval = sync_interval
        
        if git_repo_path:
            self.git_repo_path = git_repo_path
        else:
            self.git_repo_path = log_file.parent.parent.parent
        
        self.schedule_tracker = Path("data/.schedule_last_modified")
        self.last_log_time = 0
        self.last_sync_time = 0
        
        self.logger = logging.getLogger(__name__)
        self._setup_git_ssh()
        self.client = AtmoWebClient(ip=incubator_ip)
    
    def _setup_git_ssh(self):
        """Setup SSH for git."""
        ssh_key = None
        home = Path.home()
        
        for key_name in ['id_ed25519', 'id_rsa']:
            key_path = home / '.ssh' / key_name
            if key_path.exists():
                ssh_key = str(key_path)
                break
        
        if ssh_key:
            os.environ['GIT_SSH_COMMAND'] = f'ssh -i {ssh_key} -o IdentitiesOnly=yes -o StrictHostKeyChecking=no'
    
    def _git_run(self, cmd: list, timeout: int = 30) -> subprocess.CompletedProcess:
        """Run git command in repo directory."""
        original_dir = Path.cwd()
        try:
            os.chdir(self.git_repo_path)
            return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        finally:
            os.chdir(original_dir)
    
    def _backup_log_file(self):
        """Backup log file before risky operations."""
        if self.log_file.exists():
            backup = self.log_file.parent / f"{self.log_file.name}.backup"
            shutil.copy2(self.log_file, backup)
    
    def _restore_log_file(self):
        """Restore log file from backup if needed."""
        backup = self.log_file.parent / f"{self.log_file.name}.backup"
        if backup.exists() and not self.log_file.exists():
            shutil.copy2(backup, self.log_file)
    
    def git_reset_to_clean_state(self) -> bool:
        """Nuclear option: reset to clean state while preserving log file."""
        try:
            self.logger.info("⚠️  Resetting git to clean state...")
            
            # Backup log file
            self._backup_log_file()
            
            # Reset hard to HEAD
            self._git_run(['git', 'reset', '--hard', 'HEAD'])
            
            # Clean untracked files (except data/log/)
            self._git_run(['git', 'clean', '-fd', '-e', 'data/log/'])
            
            # Restore log file
            self._restore_log_file()
            
            self.logger.info("✓ Git reset complete")
            return True
            
        except Exception as e:
            self.logger.error(f"Git reset failed: {e}")
            return False
    
    def git_pull(self) -> bool:
        """Pull with automatic conflict resolution."""
        try:
            # Strategy 1: Try normal pull with stash
            status = self._git_run(['git', 'status', '--porcelain'])
            has_changes = bool(status.stdout.strip())
            
            if has_changes:
                # Backup log file first
                self._backup_log_file()
                
                # Stash changes
                self._git_run(['git', 'add', '-A'])
                self._git_run(['git', 'stash'])
            
            # Try pull
            result = self._git_run(['git', 'pull', '--rebase'])
            
            if result.returncode == 0:
                # Success! Pop stash if needed
                if has_changes:
                    pop_result = self._git_run(['git', 'stash', 'pop'])
                    if pop_result.returncode != 0:
                        # Conflict in stash pop, keep stash
                        self.logger.warning("Stash pop conflict, keeping stashed changes")
                
                if "Already up to date" not in result.stdout:
                    self.logger.info("↓ Pulled updates")
                
                self._restore_log_file()
                return True
            
            # Strategy 2: Pull failed, try reset and pull
            self.logger.warning("Pull failed, trying reset...")
            self.git_reset_to_clean_state()
            
            result = self._git_run(['git', 'pull', '--rebase'])
            if result.returncode == 0:
                self.logger.info("↓ Pulled updates (after reset)")
                self._restore_log_file()
                return True
            
            # Strategy 3: Fetch and reset to remote
            self.logger.warning("Pull still failed, syncing with remote...")
            self._git_run(['git', 'fetch', 'origin'])
            self._git_run(['git', 'reset', '--hard', 'origin/main'])
            
            self.logger.info("↓ Synced with remote (hard reset)")
            self._restore_log_file()
            return True
            
        except Exception as e:
            self.logger.error(f"Git pull error: {e}")
            self._restore_log_file()
            return False
    
    def git_push_with_retry(self, max_retries: int = 3, retry_delay: int = 5) -> bool:
        """Push with retries and automatic conflict resolution."""
        try:
            # Try push with retries
            for attempt in range(max_retries):
                result = self._git_run(['git', 'push'])
                
                if result.returncode == 0:
                    self.logger.info("↑ Pushed")
                    return True
                
                if attempt < max_retries - 1:
                    self.logger.warning(f"Push failed ({attempt + 1}/{max_retries}), retrying...")
                    time.sleep(retry_delay)
            
            # All retries failed - pull and try again
            self.logger.info("Retries failed, pulling and retrying...")
            
            # Backup log file
            self._backup_log_file()
            
            # Pull (will auto-resolve conflicts)
            self.git_pull()
            
            # Restore log file
            self._restore_log_file()
            
            # Re-add and commit log file
            log_rel = self.log_file.relative_to(self.git_repo_path)
            self._git_run(['git', 'add', str(log_rel)])
            
            # Check if there's something to commit
            status = self._git_run(['git', 'status', '--porcelain', str(log_rel)])
            if status.stdout.strip():
                commit_msg = f"Update log: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                self._git_run(['git', 'commit', '-m', commit_msg])
            
            # Try push one more time
            result = self._git_run(['git', 'push'])
            
            if result.returncode == 0:
                self.logger.info("↑ Pushed (after sync)")
                return True
            else:
                self.logger.error("Push failed after sync, will retry next cycle")
                return False
                
        except Exception as e:
            self.logger.error(f"Git push error: {e}")
            return False
    
    def git_commit_and_push(self) -> bool:
        """Commit log file and push."""
        try:
            log_rel = self.log_file.relative_to(self.git_repo_path)
            
            # Add file
            self._git_run(['git', 'add', str(log_rel)])
            
            # Check if changes exist
            status = self._git_run(['git', 'status', '--porcelain', str(log_rel)])
            
            if not status.stdout.strip():
                return True  # No changes
            
            # Commit
            commit_msg = f"Update log: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            result = self._git_run(['git', 'commit', '-m', commit_msg])
            
            if result.returncode != 0:
                self.logger.warning(f"Commit issue: {result.stderr}")
                return False
            
            # Push with retry
            return self.git_push_with_retry(max_retries=3, retry_delay=5)
            
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
            
            temp = readings.get('Temp1Read', 'N/A')
            hum = readings.get('HumRead', 'N/A')
            self.logger.info(f"📊 Temp={temp}°C, Hum={hum}%")
            
            return entry
            
        except Exception as e:
            self.logger.error(f"Read failed: {e}")
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
                    'max_hours': self.max_hours
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
            self.logger.info(f"🗑️  Trimmed {removed} entries")
        
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
            
            self.git_commit_and_push()
            
            self.last_log_time = time.time()
            
        except Exception as e:
            self.logger.error(f"Logging failed: {e}")
    
    def load_and_apply_schedule(self) -> bool:
        """Load schedule and apply the most recent setpoints to the incubator."""
        try:
            # Load the schedule file
            with open(self.schedule_file, 'r') as f:
                schedule_data = json.load(f)
            
            schedule_entries = schedule_data.get('schedule', [])
            if not schedule_entries:
                self.logger.warning("No schedule entries found")
                return False
            
            # Get the most recent entry (last in the list)
            latest_entry = schedule_entries[-1]
            setpoints = latest_entry.get('setpoints', {})
            
            if not setpoints:
                self.logger.warning("No setpoints in latest schedule entry")
                return False
            
            self.logger.info(f"📅 Applying setpoints from schedule: {setpoints}")
            
            # Apply each setpoint to the incubator
            applied = {}
            errors = []
            
            # Temperature
            if 'TempSet' in setpoints:
                try:
                    result = self.client.set_temperature(setpoints['TempSet'])
                    applied['TempSet'] = result
                    self.logger.info(f"   ✓ Temperature set to {result}°C")
                except Exception as e:
                    errors.append(f"TempSet: {e}")
                    self.logger.error(f"   ✗ Temperature failed: {e}")
            
            # Humidity
            if 'HumSet' in setpoints:
                try:
                    result = self.client.set_humidity(setpoints['HumSet'])
                    applied['HumSet'] = result
                    self.logger.info(f"   ✓ Humidity set to {result}%")
                except Exception as e:
                    errors.append(f"HumSet: {e}")
                    self.logger.error(f"   ✗ Humidity failed: {e}")
            
            # CO2 (if present)
            if 'CO2Set' in setpoints:
                try:
                    result = self.client.set_co2(setpoints['CO2Set'])
                    applied['CO2Set'] = result
                    self.logger.info(f"   ✓ CO2 set to {result}%")
                except Exception as e:
                    errors.append(f"CO2Set: {e}")
                    self.logger.error(f"   ✗ CO2 failed: {e}")
            
            # O2 (if present)
            if 'O2Set' in setpoints:
                try:
                    result = self.client.set_o2(setpoints['O2Set'])
                    applied['O2Set'] = result
                    self.logger.info(f"   ✓ O2 set to {result}%")
                except Exception as e:
                    errors.append(f"O2Set: {e}")
                    self.logger.error(f"   ✗ O2 failed: {e}")
            
            # Fan (if present)
            if 'FanSet' in setpoints:
                try:
                    result = self.client.set_fan(setpoints['FanSet'])
                    applied['FanSet'] = result
                    self.logger.info(f"   ✓ Fan set to {result}%")
                except Exception as e:
                    errors.append(f"FanSet: {e}")
                    self.logger.error(f"   ✗ Fan failed: {e}")
            
            # Read back current status to verify
            time.sleep(1)  # Brief delay to let device update
            current_status = self.client.get_status()
            
            self.logger.info("📊 Current status after applying setpoints:")
            self.logger.info(f"   Setpoints: {current_status['setpoints']}")
            self.logger.info(f"   Readings: {current_status['readings']}")
            
            if errors:
                self.logger.warning(f"⚠️  Applied with errors: {', '.join(errors)}")
                return False
            else:
                self.logger.info("✓ All setpoints applied successfully")
                return True
                
        except FileNotFoundError:
            self.logger.error(f"Schedule file not found: {self.schedule_file}")
            return False
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in schedule file: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error applying schedule: {e}")
            return False
    
    def check_schedule_update(self):
        """Check if schedule file changed and apply setpoints."""
        if not self.schedule_file.exists():
            return
        
        current_mtime = os.path.getmtime(self.schedule_file)
        
        last_mtime = None
        if self.schedule_tracker.exists():
            try:
                with open(self.schedule_tracker, 'r') as f:
                    last_mtime = float(f.read().strip())
            except:
                pass
        
        if last_mtime is None or current_mtime > last_mtime:
            self.logger.info("📅 Schedule updated! Applying setpoints...")
            
            # Apply the schedule directly
            success = self.load_and_apply_schedule()
            
            if success:
                # Update tracker to mark as processed
                self.schedule_tracker.parent.mkdir(parents=True, exist_ok=True)
                with open(self.schedule_tracker, 'w') as f:
                    f.write(str(current_mtime))
            else:
                self.logger.error("Failed to apply schedule, will retry next cycle")
    
    def sync_check(self):
        """Periodic sync check."""
        current_time = time.time()
        
        if current_time - self.last_sync_time >= self.sync_interval:
            self.git_pull()
            self.check_schedule_update()
            self.last_sync_time = current_time
    
    def run(self):
        """Main daemon loop."""
        self.logger.info("🚀 Memmert Daemon started (Autonomous Mode)")
        self.logger.info(f"   Log: {self.log_interval}s | Sync: {self.sync_interval}s")
        self.logger.info("")
        
        try:
            while True:
                current_time = time.time()
                
                if current_time - self.last_log_time >= self.log_interval:
                    self.log_data()
                
                self.sync_check()
                
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.logger.info("\n🛑 Daemon stopped")
        except Exception as e:
            self.logger.error(f"Daemon error: {e}", exc_info=True)


def main():
    """Entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Memmert Control Daemon')
    parser.add_argument('--ip', default='192.168.100.100')
    parser.add_argument('--log-interval', type=int, default=60)
    parser.add_argument('--sync-interval', type=int, default=10)
    parser.add_argument('--max-hours', type=float, default=3.0)
    parser.add_argument('--verbose', action='store_true')
    
    args = parser.parse_args()
    
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    
    daemon = MemmertDaemon(
        incubator_ip=args.ip,
        log_interval=args.log_interval,
        sync_interval=args.sync_interval,
        max_hours=args.max_hours
    )
    
    daemon.run()


if __name__ == '__main__':
    main()