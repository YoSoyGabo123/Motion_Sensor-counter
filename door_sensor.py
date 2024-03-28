import RPi.GPIO as GPIO
import time
import csv
from datetime import datetime

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

def write_to_csv(filename, data):
    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        # If file is empty, add headers
        if file.tell() == 0:
            writer.writerow(["Index", "Date and Time", "Time in Milliseconds", "Detections per Person"])
        writer.writerows(data)  # Write all data rows

def main():
    detections_within_interval = []
    start_time = time.time()
    minute_start = start_time
    
    try:
        while True:
            current_time = time.time()
            
            # Check if a minute has passed
            if current_time - minute_start >= 60:
                # Generate filename based on the current time
                filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S_people_log.csv")
                # Write the data collected in the last minute to the new file
                write_to_csv(filename, detections_within_interval)
                # Reset for the next minute
                detections_within_interval = []
                minute_start = current_time
            
            dist = distance()
            if dist < 100:  # Assuming an object is detected within 100 cm
                # Collect detection data
                detection_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                milliseconds = int((current_time - start_time) * 1000)
                detections_within_interval.append([milliseconds, detection_time, milliseconds, 1])
            
            time.sleep(0.05)  # Short sleep to reduce CPU load
    
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()

if __name__ == '__main__':
    main()



