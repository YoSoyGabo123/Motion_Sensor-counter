import RPi.GPIO as GPIO
import time
import csv
from datetime import datetime

# Set GPIO Pins
GPIO_TRIGGER = 23
GPIO_ECHO = 24
GPIO_PIR = 17  # Assuming the PIR sensor is connected to GPIO 17

# Set GPIO direction (IN / OUT)
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(GPIO_PIR, GPIO.IN)  # PIR sensor set as input

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

def write_to_csv(index, date_time, milliseconds, detections):
    with open('/mnt/data/people_log.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([index, date_time, milliseconds, detections])

def main():
    people_count = 0
    temp_count = 0
    start_time = time.time()
    csv_index = 0  # To keep track of each entry's index
    
    # Create or overwrite the CSV file with headers
    with open('/mnt/data/people_log.csv', mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Index", "Date and Time", "Time in Milliseconds", "Detections per Person"])
    
    try:
        while True:
            if GPIO.input(GPIO_PIR):  # If PIR sensor detects motion
                current_time = time.time()
                
                if current_time - start_time >= 0.7:
                    if temp_count > 0:  # If there were detections within the interval
                        people_count += 1
                        print(f"People count: {people_count}")
                        # Log to CSV
                        current_milliseconds = int((current_time - start_time) * 1000)
                        write_to_csv(csv_index, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), current_milliseconds, temp_count)
                        csv_index += 1
                    # Reset for the next interval
                    temp_count = 0
                    start_time = current_time
                
                dist = distance()
                print(f"Measured Distance = {dist} cm")
                temp_count += 1
                
                time.sleep(0.05)  # Short sleep to reduce CPU load
            else:
                # If no motion is detected by PIR, check again after a short delay
                time.sleep(0.1)
    
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()

if __name__ == '__main__':
    main()

