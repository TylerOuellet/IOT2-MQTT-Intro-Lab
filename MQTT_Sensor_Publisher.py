import paho.mqtt.client as mqtt
import time
import ADC0832
import math
import RPi.GPIO as GPIO
import json
trig = 20
echo = 21

def on_connect(client, userdata, flags, rc):
	print(f"Connected with result code {rc}")

client = mqtt.Client()
client.on_connect = on_connect
client.connect("broker.emqx.io", 1883, 60)

collected_data = {
    "temperature" : "INIT",
    "distance" : "INIT"
    }
def send(data):
    client.publish('raspberry/tylero/sensor_data', payload=data, qos=0, retain=False)
    print(f"send {data} to raspberry/tylero/sensor_data")

def init():
    ADC0832.setup()
    GPIO.setup(trig,GPIO.OUT,initial=GPIO.LOW)
    GPIO.setup(echo,GPIO.IN)

def checkdist():
	GPIO.output(trig, GPIO.HIGH)
	time.sleep(0.000015)
	GPIO.output(trig, GPIO.LOW)
	while not GPIO.input(echo):
		pass
	t1 = time.time()
	while GPIO.input(echo):
		pass
	t2 = time.time()
	return (t2-t1)*340/2

def loop():
    while True:
        res = ADC0832.getADC(0)
        if res == 0:
            collected_data["temperature"] = "N.A"
            continue
        Vr = 3.3 * float(res) / 255
        if Vr == 3.3:
            collected_data["temperature"] = "N.A"
            continue

       
        celciusTemp = float
        kelvenTemp = float

        kelvenTemp = 1/298.15 + 1/3455 * math.log((255 / res) - 1)

        kelvenTemp = 1/kelvenTemp
        celciusTemp = kelvenTemp - 273.15

        #Discard Garbage Values
        if celciusTemp >= 50 or celciusTemp<= -50:
            collected_data["temperature"] = "Discarded Value"
            print("Outlier, Descarded value")
        else:
            celciusTemp = round(celciusTemp,2)
            celciusTemp = str(celciusTemp)
            celciusTemp = celciusTemp
            collected_data["temperature"] = celciusTemp
        
        collected_data["distance"] = checkdist()
        json_data = json.dumps(collected_data)
        send(json_data)
        time.sleep(1)

if __name__ == '__main__':
    init()
    try:
        loop()
    except KeyboardInterrupt: 
        ADC0832.destroy()
        print('The end!')