#!/usr/bin/env python3
"""
Test script for Atlas I2C temperature sensors
Tests reading from RTD sensors at addresses 66, 67, 69
"""
import sys
from pathlib import Path

# Add archive to path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from AtlasI2C import AtlasI2C
    print("✓ AtlasI2C module loaded")
except ImportError as e:
    print(f"✗ Failed to import AtlasI2C: {e}")
    sys.exit(1)

import time

def test_sensor(address, sensor_num):
    """Test a single Atlas RTD sensor."""
    print(f"\nTesting Sensor {sensor_num} at address {address}...")
    print("-" * 50)
    
    try:
        # Initialize sensor
        sensor = AtlasI2C(address=address, moduletype="RTD", name=f"Sensor{sensor_num}")
        print(f"  ✓ Sensor initialized: {sensor.get_device_info()}")
        
        # Send read command
        sensor.write("R")
        time.sleep(sensor.long_timeout)
        
        # Read response
        response = sensor.read()
        print(f"  Raw response: {response}")
        
        # Parse temperature
        if "Success" in response:
            parts = response.split(":")
            if len(parts) > 1:
                temp_str = parts[-1].strip()
                temp_value = float(temp_str)
                print(f"  ✓ Temperature: {temp_value}°C")
                return temp_value
            else:
                print(f"  ⚠️  Could not parse temperature from response")
                return None
        else:
            print(f"  ✗ Sensor error: {response}")
            return None
            
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return None

def main():
    """Test all three Atlas sensors."""
    print("=" * 50)
    print("Atlas RTD Sensor Test")
    print("=" * 50)
    
    addresses = [66, 67, 69]
    results = {}
    
    for i, addr in enumerate(addresses, 1):
        temp = test_sensor(addr, i)
        results[f"Sensor{i}"] = temp
    
    print("\n" + "=" * 50)
    print("Summary:")
    print("=" * 50)
    
    for sensor_name, temp in results.items():
        if temp is not None:
            print(f"  ✓ {sensor_name}: {temp}°C")
        else:
            print(f"  ✗ {sensor_name}: Failed to read")
    
    # Test JSON format for history
    print("\n" + "=" * 50)
    print("JSON Format (for incubator_history.json):")
    print("=" * 50)
    
    readings = {
        "Temp1Read": 29.944,
        "TempSensor1Read": results.get("Sensor1"),
        "TempSensor2Read": results.get("Sensor2"),
        "TempSensor3Read": results.get("Sensor3"),
        "HumRead": 60.174,
        "CO2Read": None,
        "O2Read": None,
        "FanRead": None
    }
    
    import json
    print(json.dumps(readings, indent=2))

if __name__ == '__main__':
    main()
