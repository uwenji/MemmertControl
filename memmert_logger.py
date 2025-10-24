#!/usr/bin/env python3
"""
Memmert Data Logger - Cron-friendly version with SSH key handling
Logs incubator readings and setpoints to a rolling JSON history file and pushes to GitHub.
"""
import json
import logging
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import subprocess
import argparse

# Import from your existing atmoweb module
sys.path.insert(0, str(Path(__file__).parent / 'archive'))
from atmoweb import AtmoWebClient


class MemmertDataLogger:
    """Logger for Memmert incubator data with rolling history and GitHub sync."""
    
    def __init__(
        self,
        client: AtmoWebClient,
        log_file: Path,
        max_hours: float = 3.0,
        git_repo_path: Optional[Path] = None,
        git_auto_push: bool = True
    ):
        """
        Initialize the data logger.
        
        Args:
            client: AtmoWebClient instance
            log_file: Path to the JSON log file
            max_hours: Maximum hours of data to keep (default: 3.0)
            git_repo_path: Path to git repository (default: parent of log file)
            git_auto_push: Automatically push to GitHub after each log (default: True)
        """
        self.client = client
        self.log_file = log_file
        self.max_hours = max_hours
        self.git_auto_push = git_auto_push
        
        # Determine git repo path
        if git_repo_path:
            self.git_repo_path = git_repo_path
        else:
            # Assume the git repo is the project root
            self.git_repo_path = log_file.parent.parent.parent

        # Setup logging
        self.logger = logging.getLogger(__name__)

        # Setup SSH for git (for cron compatibility)
        self._setup_git_ssh()
        
    
    def _setup_git_ssh(self):
        """Setup SSH configuration for git to work in cron."""
        # Find SSH key
        ssh_key = None
        home = Path.home()
        
        for key_name in ['id_ed25519', 'id_rsa']:
            key_path = home / '.ssh' / key_name
            if key_path.exists():
                ssh_key = str(key_path)
                break
        
        if ssh_key:
            # Set GIT_SSH_COMMAND to use the SSH key directly
            os.environ['GIT_SSH_COMMAND'] = f'ssh -i {ssh_key} -o IdentitiesOnly=yes -o StrictHostKeyChecking=no'
            self.logger.debug(f"Using SSH key: {ssh_key}")
    
    def read_current_data(self) -> Dict[str, Any]:
        """
        Read current readings and setpoints from the incubator.
        
        Returns:
            Dictionary with timestamp, readings, and setpoints
        """
        timestamp = datetime.now().isoformat()
        
        try:
            # Get readings (actual sensor values)
            readings = self.client.get_readings()
            
            # Get setpoints (target values)
            setpoints = self.client.get_setpoints()
            
            # Get current operation mode
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
            
            self.logger.info(f"Read data: Temp={readings.get('Temp1Read', 'N/A')}°C, "
                           f"Humidity={readings.get('HumRead', 'N/A')}%")
            
            return entry
            
        except Exception as e:
            self.logger.error(f"Failed to read data from incubator: {e}")
            # Return a minimal entry with error flag
            return {
                'timestamp': timestamp,
                'error': str(e),
                'readings': {},
                'setpoints': {}
            }
    
    def load_history(self) -> Dict[str, Any]:
        """
        Load existing history from the log file.
        
        Returns:
            Dictionary with metadata and data entries
        """
        if not self.log_file.exists():
            # Create new history structure
            return {
                'metadata': {
                    'created': datetime.now().isoformat(),
                    'device_ip': self.client.base_url.replace('http://', '').replace('/atmoweb', ''),
                    'max_hours': self.max_hours,
                    'description': 'Rolling history of Memmert incubator data'
                },
                'data': []
            }
        
        try:
            with open(self.log_file, 'r') as f:
                history = json.load(f)
            
            # Ensure it has the expected structure
            if 'data' not in history:
                history['data'] = []
            if 'metadata' not in history:
                history['metadata'] = {
                    'created': datetime.now().isoformat(),
                    'device_ip': self.client.base_url.replace('http://', '').replace('/atmoweb', ''),
                    'max_hours': self.max_hours
                }
            
            return history
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse log file: {e}")
            self.logger.info("Creating new history file")
            return {
                'metadata': {
                    'created': datetime.now().isoformat(),
                    'device_ip': self.client.base_url.replace('http://', '').replace('/atmoweb', ''),
                    'max_hours': self.max_hours,
                    'note': 'Previous file was corrupted and replaced'
                },
                'data': []
            }
    
    def trim_old_data(self, data: list) -> list:
        """
        Remove data entries older than max_hours.
        
        Args:
            data: List of data entries with timestamps
            
        Returns:
            Trimmed list with only recent entries
        """
        if not data:
            return []
        
        cutoff_time = datetime.now() - timedelta(hours=self.max_hours)
        
        trimmed_data = []
        for entry in data:
            try:
                entry_time = datetime.fromisoformat(entry['timestamp'])
                if entry_time >= cutoff_time:
                    trimmed_data.append(entry)
            except (KeyError, ValueError):
                # Skip entries with invalid timestamps
                continue
        
        removed_count = len(data) - len(trimmed_data)
        if removed_count > 0:
            self.logger.info(f"Trimmed {removed_count} old entries (keeping last {self.max_hours}h)")
        
        return trimmed_data
    
    def save_history(self, history: Dict[str, Any]):
        """
        Save history to the log file.
        
        Args:
            history: Complete history dictionary to save
        """
        # Ensure log directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Update metadata
        history['metadata']['last_updated'] = datetime.now().isoformat()
        history['metadata']['total_entries'] = len(history.get('data', []))
        
        # Calculate time span
        if history['data']:
            first_time = datetime.fromisoformat(history['data'][0]['timestamp'])
            last_time = datetime.fromisoformat(history['data'][-1]['timestamp'])
            time_span = (last_time - first_time).total_seconds() / 3600  # hours
            history['metadata']['time_span_hours'] = round(time_span, 2)
        
        # Write to file
        with open(self.log_file, 'w') as f:
            json.dump(history, f, indent=2)
        
        self.logger.info(f"Saved {len(history['data'])} entries to {self.log_file}")
    
    def git_commit_and_push(self) -> bool:
        """
        Commit the log file and push to GitHub.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Change to repo directory
            original_dir = Path.cwd()
            
            try:
                os.chdir(self.git_repo_path)
                
                # Get relative path of log file from repo root
                log_file_rel = self.log_file.relative_to(self.git_repo_path)
                
                # Add the log file
                result = subprocess.run(
                    ['git', 'add', str(log_file_rel)],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode != 0:
                    self.logger.error(f"Git add failed: {result.stderr}")
                    return False
                
                # Check if there are changes to commit
                status_result = subprocess.run(
                    ['git', 'status', '--porcelain', str(log_file_rel)],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if not status_result.stdout.strip():
                    self.logger.debug("No changes to commit")
                    return True
                
                # Commit
                commit_msg = f"Update incubator log: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                result = subprocess.run(
                    ['git', 'commit', '-m', commit_msg],
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                if result.returncode != 0:
                    self.logger.error(f"Git commit failed: {result.stderr}")
                    return False
                
                # Pull first to avoid conflicts
                result = subprocess.run(
                    ['git', 'pull', '--rebase'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    self.logger.warning(f"Git pull had issues: {result.stderr}")
                    # Try to continue anyway
                
                # Push to GitHub
                result = subprocess.run(
                    ['git', 'push'],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if result.returncode != 0:
                    self.logger.error(f"Git push failed: {result.stderr}")
                    # Try pull and push again
                    self.logger.info("Trying pull and push again...")
                    subprocess.run(['git', 'pull', '--rebase'], capture_output=True, timeout=30)
                    result = subprocess.run(['git', 'push'], capture_output=True, text=True, timeout=30)
                    if result.returncode != 0:
                        return False
                
                self.logger.info("✓ Committed and pushed to GitHub")
                return True
                
            finally:
                os.chdir(original_dir)
                
        except subprocess.TimeoutExpired:
            self.logger.error("Git operation timed out")
            return False
        except Exception as e:
            self.logger.error(f"Git operation failed: {e}")
            return False
    
    def log_current_state(self):
        """
        Main logging function: read data, update history, save, and push to git.
        """
        try:
            # Read current data from incubator
            current_data = self.read_current_data()
            
            # Load existing history
            history = self.load_history()
            
            # Add new entry
            history['data'].append(current_data)
            
            # Trim old data
            history['data'] = self.trim_old_data(history['data'])
            
            # Save to file
            self.save_history(history)
            
            # Push to GitHub if enabled
            if self.git_auto_push:
                self.git_commit_and_push()
            
            self.logger.info("✓ Logging cycle complete")
            
        except Exception as e:
            self.logger.error(f"Logging cycle failed: {e}", exc_info=True)
            raise


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
        description='Log Memmert incubator data to rolling JSON history'
    )
    parser.add_argument(
        '--ip',
        default='192.168.100.100',
        help='IP address of the Memmert device (default: 192.168.100.100)'
    )
    parser.add_argument(
        '--log-file',
        type=Path,
        default=Path('data/log/incubator_history.json'),
        help='Path to log file (default: data/log/incubator_history.json)'
    )
    parser.add_argument(
        '--max-hours',
        type=float,
        default=3.0,
        help='Maximum hours of data to keep (default: 3.0)'
    )
    parser.add_argument(
        '--git-repo',
        type=Path,
        help='Path to git repository (default: auto-detect from log file)'
    )
    parser.add_argument(
        '--no-push',
        action='store_true',
        help='Disable automatic git push'
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
        
    except Exception as e:
        logger.error(f"Failed to connect to device: {e}")
        return 1
    
    # Create logger instance
    try:
        data_logger = MemmertDataLogger(
            client=client,
            log_file=args.log_file,
            max_hours=args.max_hours,
            git_repo_path=args.git_repo,
            git_auto_push=not args.no_push
        )
        
        # Log current state
        data_logger.log_current_state()
        
        return 0
        
    except Exception as e:
        logger.error(f"Logger failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    exit(main())
