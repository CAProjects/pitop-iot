from pitop import Pitop
from time import sleep
import os
import thingspeak

channel_id = 0000000 # PUT CHANNEL ID HERE
write_key  = 'xxxxxxxxxxxxxxxx' # PUT YOUR WRITE KEY HERE
channel = thingspeak.Channel(id=channel_id, api_key=write_key)

bat = Pitop().battery

while True:
    cpuTemp = round(float(open('/sys/class/thermal/thermal_zone0/temp').read()) / 1000,2)
    cpuFreq = int(int(str(os.popen('vcgencmd measure_clock arm').readline().strip('frequency(48)=')).strip())/1000000)
    cpuVolt = os.popen('vcgencmd measure_volts').readline().strip('volt=').strip()
    battery = bat.capacity
    responce = channel.update({
        'field1'    :   cpuTemp,
        'field2'    :   cpuFreq,
        'field3'    :   cpuVolt,
        'field4'    :   battery
    })
    sleep(15)
