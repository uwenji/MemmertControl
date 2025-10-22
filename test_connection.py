#!/usr/bin/env python3
"""
Quick test script for Memmert incubator connection and basic functionality.
"""
from archive.atmoweb import AtmoWebClient

def test_connection(ip='192.168.100.100'):
    """Test connection and basic operations."""
    print(f"Testing connection to {ip}...")
    print("="*60)
    
    try:
        # Create client
        client = AtmoWebClient(ip=ip)
        print("✓ Client created")
        
        # Get current readings
        print("\n📊 Current Readings:")
        readings = client.get_readings()
        for key, value in readings.items():
            if value is not None:
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: N/A")
        
        # Get current setpoints
        print("\n🎯 Current Setpoints:")
        setpoints = client.get_setpoints()
        for key, value in setpoints.items():
            if value is not None:
                print(f"  {key}: {value}")
            else:
                print(f"  {key}: N/A")
        
        # Get temperature range
        print("\n📏 Temperature Range:")
        temp_range = client.get_parameter_range('TempSet')
        if temp_range:
            print(f"  Min: {temp_range[0]}°C")
            print(f"  Max: {temp_range[1]}°C")
        else:
            print("  Not available")
        
        print("\n" + "="*60)
        print("✓ All tests passed!")
        print("Your Memmert device is ready to use with the scheduler.")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        print("\nTroubleshooting:")
        print("  1. Check IP address is correct")
        print("  2. Check ethernet cable is connected")
        print("  3. Check 'Remote Control' is enabled on device")
        print("  4. Try: ping 192.168.100.100")
        return False

if __name__ == '__main__':
    import sys
    ip = sys.argv[1] if len(sys.argv) > 1 else '192.168.100.100'
    success = test_connection(ip)
    sys.exit(0 if success else 1)
