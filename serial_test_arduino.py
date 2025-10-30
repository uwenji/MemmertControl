import serial
import time

# Adjust port if needed (/dev/ttyUSB0 for older Arduinos)
PORT = '/dev/ttyUSB0'  # or try /dev/ttyUSB0
BAUDRATE = 9600

try:
    # Open serial connection
    ser = serial.Serial(PORT, BAUDRATE, timeout=2)
    print(f"Connected to {PORT} at {BAUDRATE} baud")
    
    # CRITICAL: Wait for Arduino to reset after serial connection
    time.sleep(2)
    ser.flush()
    
    # Read startup messages
    print("Waiting for Arduino...")
    for _ in range(10):  # Try reading for a few seconds
        if ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            print(f"Arduino: {line}")
            if "READY" in line:
                break
        time.sleep(0.5)
    
    print("\nArduino ready! You can now send commands.\n")
    
    def set_pwm(channel, pulse):
        """Set PWM on a specific channel"""
        cmd = f"SET,{channel},{pulse}\n"
        ser.write(cmd.encode())
        time.sleep(0.1)
        
        # Read response
        if ser.in_waiting > 0:
            response = ser.readline().decode('utf-8', errors='ignore').strip()
            print(f"Response: {response}")
            return response
        return None
    
    def test_pca9685():
        """Run test command"""
        ser.write(b"TEST\n")
        time.sleep(0.1)
        
        # Read all responses
        while ser.in_waiting > 0:
            line = ser.readline().decode('utf-8', errors='ignore').strip()
            print(f"Arduino: {line}")
            time.sleep(0.1)
    
    # Example usage
    print("Setting channel 0 to pulse 300...")
    set_pwm(0, 300)
    
    time.sleep(1)
    
    print("\nSetting channel 1 to pulse 450...")
    set_pwm(1, 450)
    
    # Uncomment to run test
    # print("\nRunning test...")
    # test_pca9685()
    
except serial.SerialException as e:
    print(f"Error: {e}")
    print("Try: ls /dev/tty* to find correct port")
    print("Or: sudo usermod -a -G dialout $USER")
    
except KeyboardInterrupt:
    print("\nExiting...")
    
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print("Serial connection closed")
