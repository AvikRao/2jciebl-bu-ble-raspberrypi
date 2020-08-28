from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient #Import from AWS-IoT Library
import time #To create delay
from datetime import date, datetime #To get date and time
from pytz import timezone
import re
import json
import tokens

tz = timezone('US/Eastern')

myMQTTClient = AWSIoTMQTTClient("RPi4")
myMQTTClient.configureEndpoint(tokens.endpoint, 8883)
myMQTTClient.configureCredentials("/home/pi/omron_sensor/2jciebl-bu-ble-raspberrypi/AmazonRootCA1.pem", "/home/pi/omron_sensor/2jciebl-bu-ble-raspberrypi/ecabbaedab-private.pem.key", "/home/pi/omron_sensor/2jciebl-bu-ble-raspberrypi/ecabbaedab-certificate.pem.crt")
myMQTTClient.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec

with open("/home/pi/omron_sensor/2jciebl-bu-ble-raspberrypi/result.log") as results :
	lines = results.readlines()
	sequence_indexes = [i for i, x in enumerate(lines) if "Sequence" in x]

sequences = {}
for index in sequence_indexes :
	stripped = lines[index].rstrip()
	sequences[index] = int(''.join(filter(lambda c: c.isdigit(), stripped[stripped.index("Sequence") : ])))

max_sequence = 0
max_index = 0

for key, value in sequences.items(): 
	if value > max_sequence :
		max_sequence = value
		max_index = key

latest = []
for index in range(max_index - 2, max_index+11) :
	latest.append(lines[index].rstrip())
latest_str = "\n".join(latest)

sequence = float(re.findall('\d*\.?\d+', latest[2][latest[2].find("Sequence"):] )[0])
temperature = float(re.findall('\d*\.?\d+', latest[3][latest[3].find("Temperature"):])[0])
humidity = float(re.findall('\d*\.?\d+', latest[4][latest[4].find("Relative humidity"):])[0])
light = float(re.findall('\d*\.?\d+', latest[5][latest[5].find("Ambient light"):])[0])
uv = float(re.findall('\d*\.?\d+', latest[6][latest[6].find("UV index"):])[0])
pressure = float(re.findall('\d*\.?\d+', latest[7][latest[7].find("Pressure"):])[0])
sound = float(re.findall('\d*\.?\d+', latest[8][latest[8].find("Sound noise"):])[0])
discomfort = float(re.findall('\d*\.?\d+', latest[9][latest[9].find("Discomfort index"):])[0])
heatstroke = float(re.findall('\d*\.?\d+', latest[10][latest[10].find("Heat stroke"):])[0])
battery = float(re.findall('\d*\.?\d+', latest[11][latest[11].find("Battery voltage"):])[0])


print(sequence, temperature, humidity, light, uv, pressure, sound, discomfort, heatstroke, battery)

connecting_time = time.time() + 10
myMQTTClient.connect()

if time.time() < connecting_time:  #try connecting to AWS for 10 seconds

	now = datetime.now(tz) #get date and time
	current_time = now.strftime('%Y-%m-%dT%H:%M:%SZ') #get current time in string format

	current_date = now.strftime('%m/%d/%Y')
	current_clock = now.strftime('%H:%M:%S')

	myMQTTClient.publish("RPi4/connections", "Connected on {0} at {1}.".format(current_date, current_clock), 0)
	print("MQTT Client connection success!")

	payload = {
		"timestamp": current_date + " " + current_clock,
		"sequence_id": sequence, 
		"temperature": temperature,
		"relative_humidity": humidity,
		"ambient_light": light,
		"uv_index": uv,
		"pressure": pressure,
		"sound_noise": sound,
		"discomfort_index": discomfort,
		"heat_stroke": heatstroke,
		"battery_voltage": battery
	}

	myMQTTClient.publish("RPi4/testing", json.dumps(payload), 0)
	print("Payload sent!")

else:
	print("Error: Check your AWS details in the program")
	raise Exception("Timed out while trying to connect to AWS.")

