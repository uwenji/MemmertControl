import serial
import time

# Configuration
PORT = '/dev/ttyUSB0'
BAUDRATE = 9600

try:
    # Open serial connection
    ser = serial.Serial(PORT, BAUDRATE, timeout=1)
    print(f"Connected to {PORT} at {BAUDRATE} baud")
    
    # Wait for Arduino to reset
    time.sleep(2)
    ser.reset_input_buffer()  # Clear any garbage data
    
    # Read all startup messages
    print("\nWaiting for Arduino startup...")
    time.sleep(1)
    while ser.in_waiting > 0:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        print(f"  {line}")
    
    print("\n✓ Arduino ready!\n")
    
    def send_command(command):
        """Send command and wait for response"""
        # Clear input buffer before sending
        ser.reset_input_buffer()
        
        # Send command
        ser.write((command + '\n').encode())
        print(f"→ Sent: {command}")
        
        # Wait a bit for Arduino to process
        time.sleep(0.2)
        
        # Read all responses
        responses = []
        while ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            if line:
                responses.append(line)
                print(f"← Response: {line}")
            time.sleep(0.05)
        
        return responses
    
    def set_pwm(channel, pulse):
        """Set PWM on a specific channel"""
        cmd = f"SET,{channel},{pulse}"
        return send_command(cmd)
    
    # ========================================
    # Your commands here
    # ========================================
    
    print("=" * 50)
    print("Testing PCA9685 Control")
    print("=" * 50)
    
    # Test 1: Set channel 0
    print("\n[Test 1] Setting channel 0 to pulse 300")
    set_pwm(0, 300)
    time.sleep(0.5)
    
    # Test 2: Set channel 1
    print("\n[Test 2] Setting channel 1 to pulse 450")
    set_pwm(1, 450)
    time.sleep(0.5)
    
    # Test 3: Set channel 0 to different value
    print("\n[Test 3] Setting channel 0 to pulse 600")
    set_pwm(0, 600)
    time.sleep(0.5)
    
    # Test 4: Run Arduino's built-in test
    print("\n[Test 4] Running Arduino TEST command")
    send_command("TEST")
    time.sleep(3)  # Wait for test to complete
    
    # Read any remaining output
    while ser.in_waiting > 0:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if line:
            print(f"← {line}")
        time.sleep(0.05)
    
    print("\n" + "=" * 50)
    print("All tests completed!")
    print("=" * 50)

except serial.SerialException as e:
    print(f"❌ Error: {e}")
    print("\nTroubleshooting:")
    print("  1. Check cable connection")
    print("  2. Verify port: ls /dev/tty*")
    print("  3. Check permissions: sudo usermod -a -G dialout $USER")
    
except KeyboardInterrupt:
    print("\n\n⚠ Interrupted by user")
    
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("✓ Serial connection closed")