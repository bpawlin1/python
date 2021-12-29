
#
#
# This project will collect temperature,  humidity, and CO2  information using a SCD30 sensor
# and send this information to a MySQL database.
#
from __future__ import print_function
import qwiic_serlcd
import time
import sys
import time
import board
import busio
import adafruit_scd30
import datetime
import mysql.connector
import qwiic_led_stick
from digitalio import DigitalInOut, Direction, Pull
from adafruit_pm25.i2c import PM25_I2C
import serial




def particleSensor():
    
    reset_pin = None
    i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
    pm25 = PM25_I2C(i2c, reset_pin)
    print("Found PM2.5 sensor, reading data...")

    try:
        aqdata = pm25.read()
        # print(aqdata)
    except RuntimeError:
        print("Unable to read from sensor, retrying...")
        

    print()
    print("Concentration Units (standard)")
    print("---------------------------------------")
    print(
            "PM 1.0: %d\tPM2.5: %d\tPM10: %d"
             % (aqdata["pm10 standard"], aqdata["pm25 standard"], aqdata["pm100 standard"])
        )
    print("Concentration Units (environmental)")
    print("---------------------------------------")
    print(
        "PM 1.0: %d\tPM2.5: %d\tPM10: %d"
        % (aqdata["pm10 env"], aqdata["pm25 env"], aqdata["pm100 env"])
        )
    print("---------------------------------------")
    print("Particles > 0.3um / 0.1L air:", aqdata["particles 03um"])
    print("Particles > 0.5um / 0.1L air:", aqdata["particles 05um"])
    print("Particles > 1.0um / 0.1L air:", aqdata["particles 10um"])
    print("Particles > 2.5um / 0.1L air:", aqdata["particles 25um"])
    print("Particles > 5.0um / 0.1L air:", aqdata["particles 50um"])
    print("Particles > 10 um / 0.1L air:", aqdata["particles 100um"])
    print("---------------------------------------")
    


# Routine to insert temperature records into the Environmental_Data co2_data table:
def insert_record( device, datetime, temp, hum, co2, co2_rating ):
        query = "INSERT INTO co2_data (device,datetime,temp,humidity,co2,co2_rating) " \
                "VALUES (%s,%s,%s,%s,%s,%s)"
        args = (device, datetime,temp,hum,co2,co2_rating)

        try:
            conn = mysql.connector.connect( host=hostname, user=username, passwd=password, db=database )
            cursor = conn.cursor()
            cursor.execute(query, args)
            conn.commit()
            cursor.close()
            conn.close()
        except Exception as error:
            print(error)

def ledStick(co2):
    LED_stick = qwiic_led_stick.QwiicLEDStick()
    if LED_stick.begin() == False:
        print("\nThe Qwiic LED Stick isn't connected to the system. Please check your connection")

    print("\nLED Stick ready!")
    LED_stick.set_all_LED_brightness(1)
    LED_stick.LED_off()

    co2Value = co2
    co2Data = int(float(co2Value))
    print(co2Data)
    
    if co2Data < 1000:
        LED_stick.set_all_LED_color(0, 225, 0)
    elif co2Data > 1000 and  co2Data < 2000:
        LED_stick.set_all_LED_color(225, 225, 0)
    elif co2Data > 2000 and  co2Data < 5000:
        LED_stick.set_all_LED_color(225, 128, 0)
    elif co2Data > 5000:
        LED_stick.set_all_LED_color(225, 0, 0)
    

def LedScreen(co2):
    myLCD = qwiic_serlcd.QwiicSerlcd()

    if myLCD.connected == False:
        print("The Qwiic SerLCD device isn't connected to the system. Please check your connection", \
            file=sys.stderr)
        return

    myLCD.setBacklight(255, 255, 255) # Set backlight to bright white
    myLCD.setContrast(5) 
    myLCD.clearScreen() # clear the screen
   
    lcdDate = datetime.datetime.now().strftime(' %m/%d, %H:%M')
    print(lcdDate)
    
    co2Float = float(co2[1])
    co2Value = int(co2Float)
    if co2Value < 1000:
        myLCD.setBacklight(0, 255, 0)# bright green
    elif co2Value > 1000 and  co2Value < 2000:
        myLCD.setBacklight(255, 255, 0)# bright yellow
    elif co2Value > 2000 and  co2Value < 5000:
        myLCD.setBacklight(225, 128, 0)# bright Orange
    elif co2Value > 5000:
        myLCD.setBacklight(255, 0, 0)# Red

    data = co2[2]
    temp = (format(int(float(co2[1])),'.2f'))
    
    myLCD.print(" " + lcdDate)
    myLCD.setCursor(0,1)
    myLCD.print("CO2:" + data + " ")
    myLCD.print(str(temp) + "f")

    

def main():
    # Main loop
    i2c = busio.I2C(board.SCL, board.SDA)
    scd = adafruit_scd30.SCD30(i2c)
    now = datetime.datetime.now()
    date = now.strftime('%Y-%m-%d %H:%M:%S')
    co2_Data = []
    while True:
            try:
                data = scd.data_available
            except RuntimeError:
                print("Unable to read from CO2 sensor, retrying...")
            if data:
                print("Data Available!")
                temp = scd.temperature * 9/5.0 + 32
                
                humidity = scd.relative_humidity
                co2 = scd.CO2

                if scd.CO2 < 1000:
                    co2_rating = "Good"

                if scd.CO2 > 1000 and  scd.CO2 < 2000:
                    co2_rating = "Poor"

                if scd.CO2 > 2000 and  scd.CO2 < 5000:
                    co2_rating = "Bad"
                    
                if scd.CO2 > 5000:
                    co2_rating = "Very Bad"                    
            
            
            

            insert_record(device,str(date),format(temp,'.2f'),format(humidity,'.2f'), format(co2,'.2f'), co2_rating)
            print (device,str(date),format(temp,'.2f'),format(humidity,'.2f'), format(co2,'.2f'), co2_rating)

            co2_Data = format(temp,'.2f'),format(co2,'.2f'), co2_rating
            print(co2_Data)
            return co2_Data
            

if __name__=="__main__":



    while True:
        # Settings for database connection
        hostname = '127.0.0.1'
        username = 'bpawling'
        password = 'Bandit2015'
        database = 'Environmental_Data'

        device = 'dev-pi'
        co2Data = main()

        ledStick(co2Data[1])
        LedScreen(co2Data)
        particleSensor()
        time.sleep(360)
   