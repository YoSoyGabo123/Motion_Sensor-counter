import RPi.GPIO as GPIO
import time
from flask import Flask, request, redirect, url_for, session
from msal import PublicClientApplication
import requests

# Initialize Flask app
app = Flask(__name__)

# GPIO setup
GPIO_TRIGGER = 23
GPIO_ECHO = 24
GPIO.setmode(GPIO.BCM)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

# Microsoft OAuth setup
CLIENT_ID = 'd8ba1988-3e0e-40a0-897a-bcedd473cef4'
CLIENT_SECRET = 'b85b5ee5-fa50-4bc5-9f33-48935807cc64'
TENANT_ID = '481fc41f-8618-44cb-aa7e-4947d7e665a2'
AUTHORITY = f'https://login.microsoftonline.com/{TENANT_ID}'
SCOPE = ['Files.ReadWrite.All']
REDIRECT_URI = 'https://laverne-my.sharepoint.com/:x:/r/personal/gpalacios_laverne_edu/Documents/door%20counter.xlsx?d=w22c233274a5e4123b96361250327e948&csf=1&web=1&e=Oyitm5'
EXCEL_URL = 'https://laverne-my.sharepoint.com/:x:/r/personal/gpalacios_laverne_edu/Documents/door%20counter.xlsx?d=w22c233274a5e4123b96361250327e948&csf=1&web=1&e=Oyitm5'

# Initialize MSAL
msal_app = PublicClientApplication(CLIENT_ID, authority=AUTHORITY, client_credential=CLIENT_SECRET)
people_count = 0

def distance():
    """ Measure distance using ultrasonic sensor. """
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    start_time = time.time()
    stop_time = start_time
    
    while GPIO.input(GPIO_ECHO) == 0:
        start_time = time.time()
    
    while GPIO.input(GPIO_ECHO) == 1:
        stop_time = time.time()
    
    time_elapsed = stop_time - start_time
    return (time_elapsed * 34300) / 2

@app.route('/')
def home():
    """ Redirect to Microsoft login for OAuth """
    auth_url = msal_app.get_authorization_request_url(SCOPE, redirect_uri=REDIRECT_URI)
    return redirect(auth_url)

@app.route('/callback')
def callback():
    """ Handle OAuth callback, exchange code for token """
    code = request.args.get('code')
    result = msal_app.acquire_token_by_authorization_code(code, scopes=SCOPE, redirect_uri=REDIRECT_URI)
    if "access_token" in result:
        session['access_token'] = result['access_token']
        return redirect(url_for('log_data'))
    else:
        return "Error: Failed to authenticate with Microsoft."

@app.route('/log_data')
def log_data():
    """ Monitor distance and log to Excel Online when people count increases. """
    global people_count
    access_token = session.get('access_token')
    headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
    
    try:
        while True:
            dist = distance()
            print(f"Measured Distance = {dist} cm")
            if dist < 100:  # Detection threshold
                new_people_count = people_count + 1
                if new_people_count != people_count:
                    people_count = new_people_count
                    data = {'values': [[people_count]]}
                    response = requests.patch(EXCEL_URL, headers=headers, json=data)
                    if response.status_code == 200:
                        print("People count updated successfully.")
            time.sleep(1)  # Check every second
    except KeyboardInterrupt:
        print("Logging stopped by user.")
        GPIO.cleanup()
    return "Data logging completed."

if __name__ == '__main__':
    app.secret_key = 'your-secret-key'  # Needed for session management
    app.run(debug=True)
