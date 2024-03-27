import RPi.GPIO as GPIO
import time
import csv
import os
from datetime import datetime

# Sensor GPIO setup
GPIO.setmode(GPIO.BCM)
PIR_PIN = 27  # Change as per your connection
TRIG = 23  # Ultrasonic TRIG
ECHO = 24  # Ultrasonic ECHO
GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

# Function to measure distance from ultrasonic sensor
def measure_distance():
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    start_time = time.time()
    stop_time = time.time()

    while GPIO.input(ECHO) == 0:
        start_time = time.time()

    while GPIO.input(ECHO) == 1:
        stop_time = time.time()

    time_elapsed = stop_time - start_time
    distance = (time_elapsed * 34300) / 2
    return distance

# Append data to CSV file
def log_data(distance):
    with open('sensor_data.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), distance])

print("Starting sensor monitoring (CTRL+C to exit)")

try:
    while True:
        if GPIO.input(PIR_PIN):
            dist = measure_distance()
            log_data(dist)
            print(f"Motion detected! Distance: {dist} cm")
            # Delay to avoid too frequent measurements
            time.sleep(5)
except KeyboardInterrupt:
    print("Program terminated")
    GPIO.cleanup()
