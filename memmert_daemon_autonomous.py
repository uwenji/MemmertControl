#!/usr/bin/env python3
"""
Memmert Control Daemon - Fully Autonomous
Handles all git conflicts automatically, no manual intervention needed.
FIXED VERSION: Enhanced error handling for Memmert connection issues
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

# Import Atlas I2C for temperature sensors
try:
    from AtlasI2C import AtlasI2C
    ATLAS_AVAILABLE = True
except ImportError:
    ATLAS_AVAILABLE = False


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
        git_repo_path: Optional[Path] = None,
        atlas_addresses: list = [66, 67, 69]
    ):
        self.incubator_ip = incubator_ip
        self.log_file = log_file
        self.schedule_file = schedule_file
        self.max_hours = max_hours
        self.log_interval = log_interval
        self.sync_interval = sync_interval
        self.atlas_addresses = atlas_addresses
        
        if git_repo_path:
            self.git_repo_path = git_repo_path
        else:
            self.git_repo_path = log_file.parent.parent.parent
        
        self.schedule_tracker = Path("data/.schedule_last_modified")
        self.last_log_time = 0
        self.last_sync_time = 0
        
        self.logger = logging.getLogger(__name__)
        self._setup_git_ssh()
        
        # Initialize client with better error handling
        try:
            self.client = AtmoWebClient(ip=incubator_ip)
            self.logger.info(f"✓ AtmoWebClient initialized for {incubator_ip}")
        except Exception as e:
            self.logger.error(f"✗ Failed to initialize AtmoWebClient: {e}")
            self.client = None
        
        # Initialize Atlas sensors
        self.atlas_sensors = []
        if ATLAS_AVAILABLE:
            self._setup_atlas_sensors()
        else:
            self.logger.warning("⚠️  AtlasI2C not available, temperature sensors disabled")
    
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
    
    def _setup_atlas_sensors(self):
        """Initialize Atlas I2C temperature sensors."""
        try:
            for i, addr in enumerate(self.atlas_addresses, 1):
                try:
                    sensor = AtlasI2C(address=addr, moduletype="RTD", name=f"Sensor{i}")
                    # Test if sensor responds
                    sensor.write("R")
                    time.sleep(sensor.long_timeout)
                    response = sensor.read()
                    
                    if "Success" in response or "Error" not in response:
                        self.atlas_sensors.append(sensor)
                        self.logger.info(f"✓ Atlas sensor {i} initialized at address {addr}")
                    else:
                        self.logger.warning(f"⚠️  Sensor at address {addr} not responding properly")
                except Exception as e:
                    self.logger.error(f"✗ Failed to initialize sensor at address {addr}: {e}")
                    
            if self.atlas_sensors:
                self.logger.info(f"🌡️  {len(self.atlas_sensors)} Atlas temperature sensors ready")
            else:
                self.logger.warning("⚠️  No Atlas sensors initialized")
                
        except Exception as e:
            self.logger.error(f"Atlas sensor setup error: {e}")
    
    def read_atlas_sensors(self) -> Dict[str, Optional[float]]:
        """Read temperature from all Atlas RTD sensors."""
        readings = {}
        
        if not ATLAS_AVAILABLE or not self.atlas_sensors:
            return readings
        
        for i, sensor in enumerate(self.atlas_sensors, 1):
            try:
                # Send read command
                sensor.write("R")
                time.sleep(sensor.long_timeout)
                
                # Read response
                response = sensor.read()
                
                # Parse response: "Success RTD 66 Sensor1: 25.123"
                if "Success" in response:
                    # Extract temperature value from response
                    parts = response.split(":")
                    if len(parts) > 1:
                        # Strip whitespace and null bytes before converting
                        temp_str = parts[-1].strip().rstrip('\x00')
                        temp_value = float(temp_str)
                        readings[f"TempSensor{i}Read"] = round(temp_value, 3)
                    else:
                        readings[f"TempSensor{i}Read"] = None
                        self.logger.warning(f"⚠️  Could not parse sensor {i} response: {response}")
                else:
                    readings[f"TempSensor{i}Read"] = None
                    self.logger.warning(f"⚠️  Sensor {i} error: {response}")
                    
            except ValueError as e:
                readings[f"TempSensor{i}Read"] = None
                self.logger.error(f"✗ Sensor {i} value error: {e}")
            except Exception as e:
                readings[f"TempSensor{i}Read"] = None
                self.logger.error(f"✗ Sensor {i} read failed: {e}")
        
        return readings
    
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
                self._git_run(['git', 'stash', 'push', '-m', 'auto-stash'])
            
            # Pull
            result = self._git_run(['git', 'pull', '--no-edit'])
            
            if result.returncode == 0:
                self.logger.info("✓ Pull successful")
                
                if has_changes:
                    # Try to apply stash
                    apply_result = self._git_run(['git', 'stash', 'pop'])
                    
                    if apply_result.returncode != 0:
                        # Stash conflict - resolve by keeping ours
                        self.logger.warning("⚠️  Stash conflict, resolving...")
                        self._restore_log_file()
                        self._git_run(['git', 'stash', 'drop'])
                
                return True
            
            # If pull failed, check for conflicts
            if "CONFLICT" in result.stdout or "CONFLICT" in result.stderr:
                self.logger.warning("⚠️  Merge conflict detected, auto-resolving...")
                
                # Strategy 2: Accept their version for schedule, keep ours for log
                self._git_run(['git', 'checkout', '--theirs', str(self.schedule_file)])
                self._restore_log_file()
                
                # Add and continue merge
                self._git_run(['git', 'add', '.'])
                self._git_run(['git', 'commit', '--no-edit'])
                
                self.logger.info("✓ Conflicts resolved")
                return True
            
            # Strategy 3: If all else fails, reset
            self.logger.warning("⚠️  Pull failed, resetting to clean state...")
            return self.git_reset_to_clean_state()
            
        except Exception as e:
            self.logger.error(f"Pull failed: {e}")
            return False
    
    def git_push_with_retry(self, max_retries: int = 3, retry_delay: int = 5) -> bool:
        """Push with retry logic."""
        for attempt in range(max_retries):
            try:
                result = self._git_run(['git', 'push'])
                
                if result.returncode == 0:
                    self.logger.info("✓ Push successful")
                    return True
                
                # If rejected, try pull and retry
                if "rejected" in result.stderr.lower() or "non-fast-forward" in result.stderr.lower():
                    self.logger.info(f"⚠️  Push rejected, pulling... (attempt {attempt + 1}/{max_retries})")
                    
                    if self.git_pull():
                        time.sleep(retry_delay)
                        continue
                    else:
                        return False
                
                # Other push errors
                self.logger.warning(f"Push error: {result.stderr}")
                time.sleep(retry_delay)
                
            except Exception as e:
                self.logger.error(f"Push attempt {attempt + 1} failed: {e}")
                time.sleep(retry_delay)
        
        self.logger.error("✗ All push attempts failed")
        return False
    
    def git_commit_and_push(self):
        """Commit and push log changes."""
        try:
            # Add only the log file
            self._git_run(['git', 'add', str(self.log_file)])
            
            # Check if there are changes to commit
            status = self._git_run(['git', 'status', '--porcelain'])
            if not status.stdout.strip():
                return True
            
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
    
    def test_incubator_connection(self) -> bool:
        """Test if we can connect to the incubator and read data."""
        if self.client is None:
            self.logger.error("✗ Client not initialized")
            return False
        
        try:
            self.logger.info(f"🔍 Testing connection to incubator at {self.incubator_ip}...")
            
            # Try to get status
            status = self.client.get_status()
            if status and 'readings' in status and 'setpoints' in status:
                self.logger.info("✓ Connection test successful")
                self.logger.debug(f"   Status: {status}")
                return True
            else:
                self.logger.warning(f"⚠️  Got unexpected response: {status}")
                return False
                
        except Exception as e:
            self.logger.error(f"✗ Connection test failed: {e}")
            return False
    
    def read_incubator_data(self) -> Dict[str, Any]:
        """Read current data from incubator and Atlas sensors with enhanced error handling."""
        timestamp = datetime.now().isoformat()
        
        # Initialize empty readings and setpoints
        readings = {}
        setpoints = {}
        
        # Try to read from incubator
        if self.client is not None:
            try:
                self.logger.debug(f"Reading from incubator at {self.incubator_ip}...")
                
                # Get readings with error handling
                try:
                    readings = self.client.get_readings()
                    self.logger.debug(f"Got readings: {readings}")
                    
                    if readings is None:
                        self.logger.warning("⚠️  get_readings() returned None")
                        readings = {}
                    elif not isinstance(readings, dict):
                        self.logger.warning(f"⚠️  get_readings() returned unexpected type: {type(readings)}")
                        readings = {}
                        
                except Exception as e:
                    self.logger.error(f"✗ get_readings() failed: {e}", exc_info=True)
                    readings = {}
                
                # Get setpoints with error handling
                try:
                    setpoints = self.client.get_setpoints()
                    self.logger.debug(f"Got setpoints: {setpoints}")
                    
                    if setpoints is None:
                        self.logger.warning("⚠️  get_setpoints() returned None")
                        setpoints = {}
                    elif not isinstance(setpoints, dict):
                        self.logger.warning(f"⚠️  get_setpoints() returned unexpected type: {type(setpoints)}")
                        setpoints = {}
                        
                except Exception as e:
                    self.logger.error(f"✗ get_setpoints() failed: {e}", exc_info=True)
                    setpoints = {}
                    
            except Exception as e:
                self.logger.error(f"✗ Incubator read failed: {e}", exc_info=True)
        else:
            self.logger.warning("⚠️  Client not initialized, skipping incubator readings")
        
        # Read Atlas temperature sensors
        atlas_readings = self.read_atlas_sensors()
        
        # Merge Atlas readings with incubator readings
        readings.update(atlas_readings)
        
        # Get current mode
        try:
            if self.client is not None:
                mode_response = self.client.query(CurOp="")
                current_mode = mode_response.get('CurOp', 'Unknown')
            else:
                current_mode = 'No Connection'
        except Exception as e:
            self.logger.debug(f"Could not get mode: {e}")
            current_mode = 'Unknown'
        
        entry = {
            'timestamp': timestamp,
            'mode': current_mode,
            'readings': readings,
            'setpoints': setpoints
        }
        
        temp = readings.get('Temp1Read', 'N/A')
        hum = readings.get('HumRead', 'N/A')
        
        # Log Atlas sensor readings if available
        atlas_info = []
        for i in range(1, 4):
            sensor_key = f'TempSensor{i}Read'
            if sensor_key in readings and readings[sensor_key] is not None:
                atlas_info.append(f"S{i}={readings[sensor_key]}°C")
        
        if atlas_info:
            self.logger.info(f"📊 Temp={temp}°C, Hum={hum}% | {', '.join(atlas_info)}")
        else:
            self.logger.info(f"📊 Temp={temp}°C, Hum={hum}%")
        
        # Warn if Memmert readings are missing
        if temp == 'N/A' or temp is None:
            self.logger.warning("⚠️  Memmert temperature reading is missing - check incubator connection!")
        
        return entry
    
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
            
            if self.client is None:
                self.logger.error("Cannot apply schedule - client not initialized")
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
        self.logger.info("🚀 Memmert Daemon started (Autonomous Mode - FIXED)")
        self.logger.info(f"   Log: {self.log_interval}s | Sync: {self.sync_interval}s")
        self.logger.info(f"   Incubator IP: {self.incubator_ip}")
        self.logger.info(f"   Atlas sensors: {len(self.atlas_sensors)}")
        self.logger.info("")
        
        # Test connection on startup
        if not self.test_incubator_connection():
            self.logger.warning("⚠️⚠️⚠️  INCUBATOR CONNECTION FAILED  ⚠️⚠️⚠️")
            self.logger.warning("The daemon will continue but Memmert readings will be unavailable.")
            self.logger.warning("Please check:")
            self.logger.warning(f"  1. Is the incubator powered on?")
            self.logger.warning(f"  2. Is the network connection working?")
            self.logger.warning(f"  3. Is {self.incubator_ip} the correct IP address?")
            self.logger.warning(f"  4. Can you ping {self.incubator_ip}?")
            self.logger.warning("")
        
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
    
    parser = argparse.ArgumentParser(description='Memmert Control Daemon (FIXED)')
    parser.add_argument('--ip', default='192.168.100.100')
    parser.add_argument('--log-interval', type=int, default=60)
    parser.add_argument('--sync-interval', type=int, default=10)
    parser.add_argument('--max-hours', type=float, default=3.0)
    parser.add_argument('--atlas-addresses', nargs='+', type=int, default=[66, 67, 69],
                        help='I2C addresses for Atlas RTD sensors (default: 66 67 69)')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--test', action='store_true', 
                        help='Test incubator connection and exit')
    
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
        max_hours=args.max_hours,
        atlas_addresses=args.atlas_addresses
    )
    
    if args.test:
        print("\n" + "="*60)
        print("TESTING INCUBATOR CONNECTION")
        print("="*60)
        success = daemon.test_incubator_connection()
        print("="*60)
        if success:
            print("✓ Test PASSED")
            print("\nTry reading data once:")
            data = daemon.read_incubator_data()
            print(json.dumps(data, indent=2))
        else:
            print("✗ Test FAILED")
            print("\nThe incubator is not responding. Please check:")
            print(f"  - Is the incubator at {args.ip} powered on?")
            print(f"  - Can you ping {args.ip}?")
            print(f"  - Is the network connection working?")
        print("="*60)
        sys.exit(0 if success else 1)
    
    daemon.run()


if __name__ == '__main__':
    main()