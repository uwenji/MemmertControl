import board
import busio
import time

print("=== Ultra-Careful PCA9685 Initialization ===\n")

# Step 1: Software reset
print("Step 1: Software reset all PCA9685 devices...")
i2c_temp = busio.I2C(board.SCL, board.SDA)
while not i2c_temp.try_lock():
    pass

try:
    # General call reset
    i2c_temp.writeto(0x00, bytes([0x06]))
    print("  ✓ Reset command sent")
except:
    print("  ! Reset failed (may be ok)")
finally:
    i2c_temp.unlock()

time.sleep(2)  # Long wait after reset

# Step 2: Manual register programming (avoid library)
print("\nStep 2: Manual MODE1 programming...")
i2c = busio.I2C(board.SCL, board.SDA)

while not i2c.try_lock():
    pass

address = 0x70

try:
    # Read current MODE1
    result = bytearray(1)
    i2c.writeto_then_readfrom(address, bytes([0x00]), result)
    print(f"  Current MODE1: 0x{result[0]:02x}")
    time.sleep(0.5)
    
    # Set SLEEP mode (required before changing prescale)
    print("\n  Setting SLEEP mode...")
    i2c.writeto(address, bytes([0x00, 0x10]))  # MODE1, SLEEP=1
    time.sleep(1)  # LONG delay
    
    # Verify SLEEP was set
    result = bytearray(1)
    i2c.writeto_then_readfrom(address, bytes([0x00]), result)
    print(f"  MODE1 after SLEEP: 0x{result[0]:02x}")
    
    if not (result[0] & 0x10):
        print("  ✗ SLEEP bit not set - write failed!")
        raise Exception("Write failed")
    
    time.sleep(0.5)
    
    # Set prescale for 500Hz
    # prescale = round(25MHz / (4096 * 500Hz)) - 1 = 11
    print("\n  Setting prescale to 11 (for 500Hz)...")
    i2c.writeto(address, bytes([0xFE, 0x0B]))  # PRESCALE register
    time.sleep(1)  # LONG delay
    
    # Verify prescale
    result = bytearray(1)
    i2c.writeto_then_readfrom(address, bytes([0xFE]), result)
    print(f"  PRESCALE: {result[0]} (should be 11)")
    time.sleep(0.5)
    
    # Wake up and enable auto-increment
    print("\n  Waking up device...")
    i2c.writeto(address, bytes([0x00, 0xA0]))  # MODE1, AI=1, SLEEP=0
    time.sleep(1)  # LONG delay
    
    # Verify wake
    result = bytearray(1)
    i2c.writeto_then_readfrom(address, bytes([0x00]), result)
    print(f"  MODE1 final: 0x{result[0]:02x}")
    
    if result[0] & 0x10:
        print("  ⚠ Still in SLEEP mode!")
    else:
        print("  ✓ Device is awake!")
    
    time.sleep(0.5)
    
    # Try to set channel 0 to 50%
    print("\n  Setting channel 0 to 50%...")
    # LED0_ON_L, LED0_ON_H, LED0_OFF_L, LED0_OFF_H
    # ON = 0, OFF = 2048 (50% of 4096)
    i2c.writeto(address, bytes([0x06, 0x00, 0x00, 0x00, 0x08]))
    time.sleep(0.5)
    
    # Read back
    result = bytearray(4)
    i2c.writeto_then_readfrom(address, bytes([0x06]), result)
    print(f"  LED0 registers: {' '.join([f'{b:02x}' for b in result])}")
    
    print("\n✓✓✓ SUCCESS! Manual initialization worked! ✓✓✓")
    
    # Now try using the library
    print("\n\nStep 3: Try library with initialized device...")
    i2c.unlock()
    
    from adafruit_pca9685 import PCA9685
    
    # Don't reinitialize - device is already set up
    pca = PCA9685(i2c, address=0x70, reference_clock_speed=25000000)
    # The frequency is already set, don't set it again
    
    print("  ✓ Library object created")
    
    # Try controlling channels
    print("\nTesting channels...")
    pca.channels[0].duty_cycle = 16384  # 25%
    print("  ✓ Channel 0: 25%")
    time.sleep(1)
    
    pca.channels[0].duty_cycle = 49152  # 75%
    print("  ✓ Channel 0: 75%")
    time.sleep(1)
    
    pca.channels[0].duty_cycle = 0  # Off
    print("  ✓ Channel 0: Off")
    
    print("\n✓✓✓ FULL SUCCESS! PCA9685 is working! ✓✓✓")
    
    pca.deinit()
    
except OSError as e:
    print(f"\n✗ Failed at I2C operation: {e}")
    print("\nYour PCA9685 board may have a hardware issue.")
    print("The chip cannot handle writes at 100kHz I2C speed.")
    
except Exception as e:
    print(f"\n✗ Error: {e}")
    
finally:
    if i2c.try_lock():
        i2c.unlock()

print("\n=== Test Complete ===")
