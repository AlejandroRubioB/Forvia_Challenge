import RPi.GPIO as GPIO
import time
import cv2
import numpy as np
from picamera2 import Picamera2
from rpi_backlight import Backlight
piCam=Picamera2()
piCam.preview_configuration.main.size=(480,480)
piCam.preview_configuration.main.format="RGB888"
piCam.preview_configuration.align()
piCam.configure("preview")
piCam.start()
fondo = Backlight()

Video = cv2.VideoWriter("Video_Emergencia.avi",cv2.VideoWriter_fourcc(*'XVID'),10.0,(480,480))
GPIO.setmode(GPIO.BCM)

ledPin = 4
luzPin = 22
botonEmergencia = 27
botonReversa = 12
TRIG_PIN = 23
ECHO_PIN = 24
clk = 17
dt = 13
buzzer=21
ldr = 26                                                 
TRIG_PIN2 = 25
ECHO_PIN2 = 8

sleepTime=.01
Tiempo =0.0 
Grabar = 0
counter = 0
dist=0
distancia=0
historial_fondo=0
GPIO.setup(ledPin, GPIO.OUT)
GPIO.setup(luzPin, GPIO.OUT)
GPIO.setup(buzzer, GPIO.OUT)

GPIO.setup(botonEmergencia, GPIO.IN)
GPIO.setup(botonReversa, GPIO.IN)
GPIO.setup(ldr, GPIO.IN)

GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)
GPIO.setup(TRIG_PIN2, GPIO.OUT)
GPIO.setup(ECHO_PIN2, GPIO.IN)

GPIO.setup(clk, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(dt, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

clkLastState= GPIO.input(clk)
GPIO.output(ledPin,False)
GPIO.output(buzzer,False)

def Distancia():
	GPIO.output(TRIG_PIN, True)
	time.sleep(0.00001)
	GPIO.output(TRIG_PIN, False)
	pulse_start_time = time.time()
	pulse_end_time = time.time()
	while GPIO.input(ECHO_PIN) == 0:
		pulse_start_time = time.time()
	while GPIO.input(ECHO_PIN) == 1:
		pulse_end_time = time.time()
	pulse_duration = pulse_end_time - pulse_start_time
	distance = (pulse_duration * 34300) / 2 	
	distance = int(distance)
	if distance <300:
		return (distance)
	else:
		 return (0)
		 
def Distancia2():
	GPIO.output(TRIG_PIN2, True)
	time.sleep(0.00001)
	GPIO.output(TRIG_PIN2, False)
	pulse_start_time = time.time()
	pulse_end_time = time.time()
	while GPIO.input(ECHO_PIN2) == 0:
		pulse_start_time = time.time()
	while GPIO.input(ECHO_PIN2) == 1:
		pulse_end_time = time.time()
	pulse_duration = pulse_end_time - pulse_start_time
	distance = (pulse_duration * 34300) / 2	
	distance = int(distance)
	if distance <300:
		return (distance)
	else:
		 return (0)
		

def GuardarVideo():
	frame=piCam.capture_array()
	cv2.imshow('Grabar',frame)
	cv2.moveWindow('Grabar',160,0)
	Video.write(frame)
	
	
while True:
	clkState = GPIO.input(clk)
	dtState = GPIO.input(dt)
	
	centro=(200+2*counter,240)
	centro2=(280+2*counter,240)	
	if clkState != clkLastState:
		if dtState == clkState:
			counter += 1
		else:
			counter -=3
		print (counter)
	clkLastState = clkState
	
	frame=piCam.capture_array()

	cv2.line(frame,(10,100),(300,100),(255,255,255),1)
	cv2.line(frame,(10,200),(300,200),(255,255,255),1)
	cv2.line(frame,(10,300),(300,300),(255,255,255),1)
	if(counter >=0):
			cv2.ellipse(frame,centro,(2*counter,100),0,90,270,(0,0,255),5)
			cv2.ellipse(frame,centro2,(2*counter,100),0,90,270,(0,0,255),5)
	else:
			cv2.ellipse(frame,centro,(-2*counter,100),180,90,270,(0,0,255),5)
			cv2.ellipse(frame,centro2,(-2*counter,100),180,90,270,(0,0,255),5)	
			
	if GPIO.input(ldr)==True and historial_fondo==0:

		print("no  hay luz")
		fondo.brightness = 100
		GPIO.output(luzPin,True)

		historial_fondo=1
	if GPIO.input(ldr)== False and historial_fondo==1:

		historial_fondo=0
		print("si luz")
		GPIO.output(luzPin,False)
		fondo.brightness = 50
		
	if GPIO.input(botonEmergencia)==True:
		Grabar=1
		cv2.destroyAllWindows()
		while Grabar ==1 and Tiempo<1.7:
			GPIO.output(ledPin,True)
			GuardarVideo()		
			key=cv2.waitKey(1)		
			time.sleep(sleepTime)
			Tiempo = Tiempo + sleepTime	
		cv2.destroyAllWindows()
		GPIO.output(ledPin,False)
		Tiempo =0
		Grabar=0
	else:
		if GPIO.input(botonReversa)==True:
			GPIO.output(ledPin,True)
			distancia=Distancia()
			distancia2=Distancia2()
			
			if distancia2>=distancia:
				distanciaMenor=distancia
			if distancia>distancia2:
				distanciaMenor=distancia2
					
			if distanciaMenor != 0:
				texto = "Distance to object: "+str(distanciaMenor) +" cm"
				cv2.putText(frame,texto,(0,50),cv2.FONT_HERSHEY_SIMPLEX,1,(253,255,0),1)	
			else:
				distanciaMenor = 3232323			
			cv2.imshow('video',frame)
			cv2.moveWindow('video',160,0)
							
			dist= dist+2
			
			if  dist>=float(distanciaMenor):
				GPIO.output(buzzer,True)
				dist=0
			else:
				GPIO.output(buzzer,False)
			time.sleep(.001)
		else:
			cv2.destroyAllWindows()
			GPIO.output(buzzer,False)			
			GPIO.output(ledPin,False)
			dist =0
		
	key=cv2.waitKey(1) & 0XFF
	if key == '27':
		break	

GPIO.output(ledPin,False)
GPIO.output(buzzer,False)	
Video.release()
GPIO.cleanup()
cam.release()
cv2.destroyAllWindows()



