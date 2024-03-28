import RPi.GPIO as GPIO
import time

# Set GPIO Pins
GPIO_TRIGGER = 23
GPIO_ECHO = 24

# Set GPIO direction (IN / OUT)
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

def distance():
    # Set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
    # Set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    StartTime = time.time()
    StopTime = time.time()
    # Save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
    # Save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
    # Time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # Multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
    return distance

def main():
    people_count = 0
    temp_count = 0
    start_time = time.time()
    
    try:
        while True:
            if time.time() - start_time >= 0.7:
                # Every 0.7 seconds, update the people_count with temp_count
                # Here, you can also apply any logic to adjust the count, e.g., averaging or summing
                if temp_count > 0:  # Assuming any detection within 0.7 seconds counts as one person
                    people_count += 1
                    print(f"People count: {people_count}")
                # Reset temp_count and start_time for the next 0.7-second interval
                temp_count = 0
                start_time = time.time()
            
            dist = distance()
            print(f"Measured Distance = {dist} cm")
            if dist < 100:
                print("Person detected!")
                temp_count += 1
                # Instead of sleeping here, you control the rate of detection with the measurement interval sleep
            time.sleep(0.0005)  # Measurement interval

    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()

if __name__ == '__main__':
    main()

