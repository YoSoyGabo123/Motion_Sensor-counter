import RPi.GPIO as GPIO
import time
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, db

# Initialize Firebase Admin
cred = credentials.Certificate('path_to_your_firebase_service_account_key.json')
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://your-firebase-project-id.firebaseio.com/'
})

# Set GPIO Pins for the ultrasonic sensor
GPIO_TRIGGER = 23
GPIO_ECHO = 24

# Set GPIO direction (IN / OUT)
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

def measure_distance():
    """Measure distance using the ultrasonic sensor."""
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    StartTime = time.time()
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()

    StopTime = time.time()
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    TimeElapsed = StopTime - StartTime
    return (TimeElapsed * 34300) / 2  # Distance in centimeters

def main():
    people_count = 0
    last_detection_time = time.time()
    detection_threshold = 100  # distance threshold in centimeters
    debounce_time = 2  # seconds to wait before counting another person

    print("Starting measurement...")

    try:
        while True:
            dist = measure_distance()
            print(f"Measured Distance: {dist:.1f} cm")

            current_time = time.time()
            if dist < detection_threshold and (current_time - last_detection_time) > debounce_time:
                people_count += 1
                last_detection_time = current_time
                print(f"People count: {people_count}")

                # Log to Firebase Realtime Database
                db.reference('people_counter').set({
                    'count': people_count,
                    'timestamp': datetime.now().isoformat()
                })

            time.sleep(0.1)  # Brief pause to decrease CPU load

    except KeyboardInterrupt:
        print("Measurement stopped by User")
    finally:
        GPIO.cleanup()

if __name__ == '__main__':
    main()
