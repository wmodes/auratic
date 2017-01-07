import serial
ser = serial.Serial('/dev/ttyUSB0', 9600)

while True:
	num = raw_input("Enter integer 1-9: ")
	print "Sending serial signal. Watch for arduino blink."
	ser.write(num)

