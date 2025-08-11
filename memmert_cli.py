#!/usr/bin/env python3
"""
Command-line interface for Memmert incubator control.

Usage:
    Apply settings:
        python3 memmert_cli.py --ip 192.168.100.100 apply settings.json
    
    Read status:
        python3 memmert_cli.py --ip 192.168.100.100 status
    
    Monitor continuously:
        python3 memmert_cli.py --ip 192.168.100.100 monitor --interval 30
"""
import argparse
import json
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

from atmoweb import AtmoWebClient


class MemmertController:
    """High-level controller for Memmert incubator operations."""
    
    def __init__(self, client: AtmoWebClient):
        """
        Initialize controller with AtmoWeb client.
        
        Args:
            client: Configured AtmoWebClient instance
        """
        self.client = client
        self.setter_map = {
            'TempSet': self.client.set_temperature,
            'HumSet': self.client.set_humidity,
            'CO2Set': self.client.set_co2,
            'O2Set': self.client.set_o2,
            'FanSet': self.client.set_fan
        }
    
    def apply_settings(self, settings: Dict[str, float]) -> Dict[str, Any]:
        """
        Apply settings from a dictionary.
        
        Args:
            settings: Dictionary of parameter names to values
            
        Returns:
            Dictionary with 'applied' and 'errors' sections
        """
        applied = {}
        errors = {}
        
        for key, value in settings.items():
            setter = self.setter_map.get(key)
            
            if not setter:
                errors[key] = f"Unknown parameter: {key}"
                continue
            
            try:
                result = setter(float(value))
                applied[key] = result
                print(f"✓ {key}: {value} → {result}")
            except ValueError as e:
                errors[key] = str(e)
                print(f"✗ {key}: {e}")
            except KeyError as e:
                errors[key] = str(e)
                print(f"✗ {key}: Parameter not supported")
            except Exception as e:
                errors[key] = f"Unexpected error: {e}"
                print(f"✗ {key}: {e}")
        
        return {'applied': applied, 'errors': errors}
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get complete system status.
        
        Returns:
            Status dictionary with timestamp, setpoints, and readings
        """
        return {
            'timestamp': datetime.now().isoformat(),
            'setpoints': self.client.get_setpoints(),
            'readings': self.client.get_readings()
        }
    
    def save_status(self, filepath: Path) -> None:
        """
        Save current status to a JSON file.
        
        Args:
            filepath: Path to save the status file
        """
        status = self.get_status()
        filepath.write_text(json.dumps(status, indent=2))
        print(f"\n📄 Status saved to: {filepath.resolve()}")
    
    def monitor(self, interval: int = 30, duration: Optional[int] = None) -> None:
        """
        Monitor the incubator continuously.
        
        Args:
            interval: Seconds between readings
            duration: Total monitoring duration in seconds (None for infinite)
        """
        start_time = time.time()
        print(f"\n🔍 Monitoring started (interval: {interval}s)")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                if duration and (time.time() - start_time) > duration:
                    break
                
                status = self.get_status()
                self._print_monitor_line(status)
                
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n\n✋ Monitoring stopped")
    
    def _print_monitor_line(self, status: Dict[str, Any]) -> None:
        """Print a single monitoring line."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        readings = status['readings']
        
        # Format readings, showing only non-null values
        parts = [f"{timestamp}"]
        
        if readings.get('Temp1Read') is not None:
            parts.append(f"T:{readings['Temp1Read']:.1f}°C")
        if readings.get('HumRead') is not None:
            parts.append(f"H:{readings['HumRead']:.1f}%")
        if readings.get('CO2Read') is not None:
            parts.append(f"CO₂:{readings['CO2Read']:.1f}%")
        if readings.get('O2Read') is not None:
            parts.append(f"O₂:{readings['O2Read']:.1f}%")
        if readings.get('FanRead') is not None:
            parts.append(f"Fan:{readings['FanRead']:.0f}%")
        
        print(" | ".join(parts))


class CLI:
    """Command-line interface handler."""
    
    @staticmethod
    def create_parser() -> argparse.ArgumentParser:
        """Create and configure the argument parser."""
        parser = argparse.ArgumentParser(
            description="Memmert incubator control interface",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        # Connection parameters
        parser.add_argument(
            "--ip", 
            required=True, 
            help="Incubator IP address"
        )
        parser.add_argument(
            "--port", 
            type=int, 
            default=80,
            help="HTTP port (default: 80)"
        )
        parser.add_argument(
            "--timeout", 
            type=int, 
            default=5,
            help="Connection timeout in seconds (default: 5)"
        )
        
        # Commands
        subparsers = parser.add_subparsers(dest="command", required=True)
        
        # Apply command
        apply_parser = subparsers.add_parser(
            "apply",
            help="Apply settings from JSON file"
        )
        apply_parser.add_argument(
            "file",
            type=Path,
            help="JSON file with settings"
        )
        apply_parser.add_argument(
            "--save-status",
            action="store_true",
            help="Save status after applying settings"
        )
        
        # Status command
        status_parser = subparsers.add_parser(
            "status",
            help="Read current status"
        )
        status_parser.add_argument(
            "--output",
            "-o",
            type=Path,
            default=Path("status.json"),
            help="Output file for status (default: status.json)"
        )
        status_parser.add_argument(
            "--no-save",
            action="store_true",
            help="Don't save status to file"
        )
        
        # Monitor command
        monitor_parser = subparsers.add_parser(
            "monitor",
            help="Monitor incubator continuously"
        )
        monitor_parser.add_argument(
            "--interval",
            "-i",
            type=int,
            default=30,
            help="Seconds between readings (default: 30)"
        )
        monitor_parser.add_argument(
            "--duration",
            "-d",
            type=int,
            help="Total monitoring duration in seconds"
        )
        
        return parser
    
    @staticmethod
    def load_settings(filepath: Path) -> Dict[str, float]:
        """Load settings from JSON file."""
        try:
            content = json.loads(filepath.read_text())
            if not isinstance(content, dict):
                raise ValueError("Settings file must contain a JSON object")
            return content
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {filepath}: {e}")
        except FileNotFoundError:
            raise ValueError(f"Settings file not found: {filepath}")
    
    @staticmethod
    def print_status(status: Dict[str, Any]) -> None:
        """Pretty-print status information."""
        print("\n" + "="*50)
        print(f"📊 INCUBATOR STATUS - {status['timestamp']}")
        print("="*50)
        
        print("\n📋 SETPOINTS:")
        for key, value in status['setpoints'].items():
            if value is not None:
                unit = CLI._get_unit(key)
                print(f"  {key:<12}: {value:>6.1f} {unit}")
            else:
                print(f"  {key:<12}: N/A")
        
        print("\n📈 CURRENT READINGS:")
        for key, value in status['readings'].items():
            if value is not None:
                unit = CLI._get_unit(key)
                print(f"  {key:<12}: {value:>6.1f} {unit}")
            else:
                print(f"  {key:<12}: N/A")
        
        print("="*50 + "\n")
    
    @staticmethod
    def _get_unit(key: str) -> str:
        """Get the appropriate unit for a parameter."""
        if 'Temp' in key:
            return '°C'
        elif 'Hum' in key:
            return '% RH'
        elif 'CO2' in key or 'O2' in key:
            return '%'
        elif 'Fan' in key:
            return '%'
        return ''


def main():
    """Main entry point."""
    cli = CLI()
    parser = cli.create_parser()
    args = parser.parse_args()
    
    try:
        # Create client and controller
        client = AtmoWebClient(
            ip=args.ip,
            port=args.port,
            timeout=args.timeout
        )
        controller = MemmertController(client)
        
        # Execute command
        if args.command == "apply":
            print(f"\n🔧 Applying settings from: {args.file}")
            settings = cli.load_settings(args.file)
            
            print("\n📝 Settings to apply:")
            for key, value in settings.items():
                print(f"  {key}: {value}")
            print()
            
            result = controller.apply_settings(settings)
            
            if result['errors']:
                print(f"\n⚠️  {len(result['errors'])} errors occurred")
            
            if args.save_status or not args.__dict__.get('no_save', True):
                controller.save_status(Path("status.json"))
        
        elif args.command == "status":
            status = controller.get_status()
            cli.print_status(status)
            
            if not args.no_save:
                controller.save_status(args.output)
        
        elif args.command == "monitor":
            controller.monitor(
                interval=args.interval,
                duration=args.duration
            )
    
    except KeyboardInterrupt:
        print("\n\n🛑 Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()