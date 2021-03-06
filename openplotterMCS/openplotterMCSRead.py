#!/usr/bin/env python

# This file is part of Openplotter.
# Copyright (C) 2019 by GeDaD <https://github.com/Thomas-GeDaD/openplotter-MCS>
# 
# Openplotter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
# Openplotter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openplotter. If not, see <http://www.gnu.org/licenses/>.
import socket, time, random, os , statistics, pigpio
from openplotterSettings import conf
import RPi.GPIO as GPIO
from time import perf_counter

def main():
	time.sleep(30)
	try:
		conf2 = conf.Conf()
		value = conf2.get('MCS', 'sending')
		port = conf2.get('MCS', 'MCSConn1')
		portstalk = conf2.get('MCS', 'MCSConn2')
		Sensor = conf2.get('MCS', 'owiresensors')
		config_osensors = eval (Sensor)
		wic_state = conf2.get('MCS', 'wic_state')
		wic1 = conf2.get('MCS', 'wic1')
		wic1 = list(wic1.split(","))
		wic2 = conf2.get('MCS', 'wic2')
		wic2 = list(wic2.split(","))		
		wic3 = conf2.get('MCS', 'wic3')		
		wic3 = list(wic3.split(","))
		wic4 = conf2.get('MCS', 'wic4')
		wic4 = list(wic4.split(","))
		st1state=False
	except Exception as e: print (str(e))
	
	if wic_state == "True":
		GPIO.setmode(GPIO.BCM)
		try:
			os.system("sudo pigpiod")
			time.sleep(2)
		except: pass
		try:
			st1read =pigpio.pi()
		except: pass

		try:
			st1read.bb_serial_read_close(19) #close if already run
		except: pass
		try:
			st1read.bb_serial_read_close(16) #close if already run
		except: pass
		try:
			st1read.bb_serial_read_close(26) #close if already run
		except: pass
		try:
			st1read.bb_serial_read_close(20) #close if already run
		except: pass
		
		
		
		if wic1[0]=="frequency":
			measure1=MeasureFrequency(19)
			measure1.start()
			average1=MovingAverage(0.6)
		if wic1[0]=="Seatalk_1":
			st1gpio=19
			try:
				st1read.bb_serial_read_open(st1gpio, 4800,9)
			except:pass
			st1state=True

		if wic2[0]=="frequency":
			measure2=MeasureFrequency(16)
			measure2.start()
			average2=MovingAverage(0.6)
		if wic2[0]=="Seatalk_1":
			st1gpio=16
			try:
				st1read.bb_serial_read_open(st1gpio, 4800,9)
			except: pass
			st1state=True
			
		if wic3[0]=="frequency":
			measure3=MeasureFrequency(26)
			measure3.start()
			average3=MovingAverage(0.6)
		if wic3[0]=="Seatalk_1":
			st1gpio=26
			try:
				st1read.bb_serial_read_open(st1gpio, 4800,9)
			except: pass
			st1state=True
			
		if wic4[0]=="frequency":
			measure4=MeasureFrequency(20)
			measure4.start()
			average4=MovingAverage(0.6)
		if wic4[0]=="Seatalk_1":
			st1gpio=20
			try:
				st1read.bb_serial_read_open(st1gpio, 4800,9)
			except: pass
			st1state=True
			
#initiate socket
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	if st1state:
		sockst1 = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	
	if value == '1':
		while True:
			values=""
			#WIC readings:
			if wic_state == "True":	
				#print ("wic state true")
				if wic1[0]=="frequency":
					freq1=measure1.frequency()
					average1.add(freq1)
					freq1_=average1.value()
					freq1_=freq1_*float(wic1[2])
					freq1_=round(freq1_,2)
					values += '{"path":"'+ str(wic1[1]) +'","value":' +str(freq1_)+ '},'
    
				if wic2[0]=="frequency":
					freq2=measure2.frequency()
					average2.add(freq2)
					freq2_=average2.value()
					freq2_=freq2_*float(wic2[2])
					freq2_=round(freq2_,2)
					values += '{"path":"'+ str(wic2[1]) +'","value":' +str(freq2_)+ '},'
    
				if wic3[0]=="frequency":
					freq3=measure3.frequency()
					average3.add(freq3)
					freq3_=average3.value()
					freq3_=freq3_*float(wic3[2])
					freq3_=round(freq3_,2)
					values += '{"path":"'+ str(wic3[1]) +'","value":' +str(freq3_)+ '},'
			
				if wic4[0]=="frequency":
					freq4=measure4.frequency()
					average4.add(freq4)
					freq4_=average4.value()
					freq4_=freq4_*float(wic4[2])
					freq4_=round(freq4_,2)
					values += '{"path":"'+ str(wic4[1]) +'","value":' +str(freq4_)+ '},'
			
			#1-wire readings
			for i in config_osensors:
				try:
					x= os.listdir("/sys/bus/w1/devices")
					if i[0] in x:
						foo = open("/sys/bus/w1/devices/"+ i[0] +"/w1_slave","r")
						data = foo.read ()
						foo.close()
						spos=data.find("t=")
						tempx=(data[spos+2:-1])
						temp = int(tempx)/1000
						temp = temp + 273.15
					else:
						temp=str('"no data"')
					values += '{"path":"'+ str(i[2]) +'","value":' +str(temp)+ '},'
				except Exception as e: print (str(e))			

			if values:
				values=values[0:-1]
				SignalK = '{"updates":[{"$source":"OpenPlotter.MCS","values":['+values+']}]}\n'	
				sock.sendto(SignalK.encode('utf-8'), ('127.0.0.1', int(port)))
				#print (SignalK)
			#seatalk1 readings
			if st1state:
				data=""
				try:
					out=(st1read.bb_serial_read(st1gpio))
					out0=out[0]
					#print(portstalk)
					if out0>0:
						out_data=out[1]
						x=0
						while x < out0:
							if out_data[x+1] ==0:
								string1=str(hex(out_data[x]))
								data= data+string1[2:]+ ","
							else:
								data=data[0:-1]
								data="$STALK,"+data+"\r\n"
								sockst1.sendto(data.encode('utf-8'), ('127.0.0.1', int(portstalk)))
								#print (data)
								string2=str(hex(out_data[x]))
								data=string2[2:]+ ","
							x+=2
				except  Exception as e: print (str(e))
			time.sleep (0.2)
	

class MeasureFrequency(object):

    def __init__(self, channel):
        GPIO.setup(channel, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        self.channel = channel
        self.pulse1 = 0
        self.pulsetime1=perf_counter()
        self.freq=0
        self.data = []

    def _interrupt_counter(self, channel):
        diff = perf_counter()-self.pulsetime1
        self.pulsetime1=perf_counter()
        self.data.append(diff)
        

    def frequency(self):
        sum_=0
        count=0
        freq=0
        try:
            freq=statistics.mean(self.data)
            freq=1/freq
        except:
            freq=0
        self.data=[]
        return freq

    def start(self):
        GPIO.add_event_detect(self.channel, GPIO.RISING,
                              callback=self._interrupt_counter,
                              bouncetime=1)
class MovingAverage:
    def __init__(self,factor):
        self.factor=float(factor)
        self.current=0

    def add(self,value):
        fv=float(value)
        diff=fv-self.current
        self.current+=self.factor*diff

    def value(self):
        return self.current
		


if __name__ == '__main__':
	main()
	
			
