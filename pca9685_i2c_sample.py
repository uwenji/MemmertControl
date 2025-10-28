import time
import board
import busio
from adafruit_pca9685 import PCA9685

# Initialize I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create PCA9685 object with address 0x70
pca = PCA9685(i2c, address=0x70)  # <-- Specify your address here

# Set PWM frequency for LDD drivers
pca.frequency = 500

# Control channel 0
pca.channels[0].duty_cycle = 32768  # 50% intensity

time.sleep(2)

# Turn off
pca.channels[0].duty_cycle = 0

# Clean up
pca.deinit()
