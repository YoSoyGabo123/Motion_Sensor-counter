import RPi.GPIO as GPIO
import time

# GPIO setup
GPIO.setmode(GPIO.BCM)
PIR_PIN = 27  # Change this to the pin you're using
GPIO.setup(PIR_PIN, GPIO.IN)

people_count = 0

def motion_detected(PIR_PIN):
    global people_count
    people_count += 1
    print(f"Motion detected! People count: {people_count}")

print("PIR Module Test (CTRL+C to exit)")
time.sleep(2)
print("Ready")

try:
    GPIO.add_event_detect(PIR_PIN, GPIO.RISING, callback=motion_detected)
    # Use an infinite loop to keep the script running
    while True:
        time.sleep(100)
except KeyboardInterrupt:
    print("Quit")
    GPIO.cleanup()
