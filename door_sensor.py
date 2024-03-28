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
    # [The distance function remains unchanged]
    # [Insert the distance function code here]

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
            pir_status = GPIO.input(GPIO_PIR)
            if pir_status:  # If PIR sensor detects motion
                dist = distance()
                current_time = time.time()
                temp_count += 1  # Increment temp_count for each detection
                
                # Every 0.7 seconds, check the detection count
                if current_time - start_time >= 0.7:
                    if temp_count > 0:  # If there were detections
                        people_count += 1
                        print(f"People count: {people_count}")
                        # Log to CSV
                        current_milliseconds = int((current_time - start_time) * 1000)
                        write_to_csv(csv_index, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), current_milliseconds, temp_count)
                        csv_index += 1
                    temp_count = 0  # Reset temp_count
                    start_time = current_time  # Reset the start time for the next interval

                time.sleep(0.05)  # Short sleep to reduce CPU load

    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()

if __name__ == '__main__':
    main()

