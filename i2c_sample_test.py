import board
import busio
import time

print("=== Low-Level PCA9685 Test ===\n")

i2c = busio.I2C(board.SCL, board.SDA)

def read_register(address, register):
    """Read a single register"""
    while not i2c.try_lock():
        pass
    try:
        result = bytearray(1)
        i2c.writeto_then_readfrom(address, bytes([register]), result)
        return result[0]
    except Exception as e:
        return None
    finally:
        i2c.unlock()

def write_register(address, register, value):
    """Write a single register"""
    while not i2c.try_lock():
        pass
    try:
        i2c.writeto(address, bytes([register, value]))
        time.sleep(0.01)  # Small delay
        return True
    except Exception as e:
        return False
    finally:
        i2c.unlock()

address = 0x70

print("Step 1: Read MODE1 register (0x00)")
mode1 = read_register(address, 0x00)
if mode1 is not None:
    print(f"  ✓ MODE1 = 0x{mode1:02x}")
else:
    print("  ✗ Cannot read MODE1")
    exit(1)

print("\nStep 2: Read MODE2 register (0x01)")
mode2 = read_register(address, 0x01)
if mode2 is not None:
    print(f"  ✓ MODE2 = 0x{mode2:02x}")
else:
    print("  ✗ Cannot read MODE2")

print("\nStep 3: Try to write MODE1 (set SLEEP bit)")
if write_register(address, 0x00, 0x10):  # Set sleep mode
    print("  ✓ Write successful")
    time.sleep(0.1)
    
    # Read it back
    mode1_new = read_register(address, 0x00)
    if mode1_new is not None:
        print(f"  ✓ MODE1 now = 0x{mode1_new:02x}")
        if mode1_new & 0x10:
            print("  ✓ SLEEP bit is set - write worked!")
        else:
            print("  ✗ SLEEP bit NOT set - write didn't stick")
    else:
        print("  ✗ Cannot read back MODE1 - device crashed!")
else:
    print("  ✗ Write failed")

print("\nStep 4: Try to set prescaler (this is what fails)")
# Setting frequency requires writing to PRESCALE register
# First must set SLEEP mode
if write_register(address, 0x00, 0x10):  # SLEEP
    time.sleep(0.01)
    print("  ✓ Entered SLEEP mode")
    
    # Calculate prescale for 500Hz: prescale = 25MHz / (4096 * 500Hz) - 1 = 11
    prescale = 11
    
    if write_register(address, 0xFE, prescale):  # PRESCALE register
        print(f"  ✓ Wrote PRESCALE = {prescale}")
        time.sleep(0.01)
        
        # Wake up
        if write_register(address, 0x00, 0x00):  # Clear SLEEP
            print("  ✓ Exited SLEEP mode")
            time.sleep(0.005)
            
            # Check if device is still alive
            mode1_final = read_register(address, 0x00)
            if mode1_final is not None:
                print(f"  ✓ Device still responding! MODE1 = 0x{mode1_final:02x}")
                print("\n✓✓✓ SUCCESS! Frequency setting worked! ✓✓✓")
            else:
                print("  ✗ Device crashed after setting frequency")
        else:
            print("  ✗ Failed to exit SLEEP mode")
    else:
        print("  ✗ Failed to write PRESCALE - device may have crashed")
else:
    print("  ✗ Failed to enter SLEEP mode")

print("\n=== Test Complete ===")
