
#
#
# This project will collect temperature,  humidity, and CO2  information using a SCD30 sensor
# and send this information to a MySQL database.
#
from __future__ import print_function
#import qwiic_serlcd
import time
import sys
#import busio
import mysql.connector
#import qwiic_led_stick
#import serial

#
#
#
#
#def ledStick(co2):
#    LED_stick = qwiic_led_stick.QwiicLEDStick()
#    if LED_stick.begin() == False:
#        print("\nThe Qwiic LED Stick isn't connected to the system. Please check your connection")
#
#    #print("\nLED Stick ready!")
#    LED_stick.set_all_LED_brightness(1)
#    LED_stick.set_all_LED_color(70,130,180)
#    try:
#        if len(co2) > 1 :
#            co2Value = co2
#            co2Data = int(float(co2Value))
#            #print(co2Data)
#
#            if co2Data < 1000:
#                LED_stick.set_all_LED_color(0, 225, 0)
#            elif co2Data > 1000 and  co2Data < 2000:
#                LED_stick.set_all_LED_color(225, 225, 0)
#            elif co2Data > 2000 and  co2Data < 5000:
#                LED_stick.set_all_LED_color(225, 128, 0)
#            elif co2Data > 5000:
#                LED_stick.set_all_LED_color(225, 0, 0)
#    except Exception as e:
#        print(e)
#        LED_stick.set_all_LED_color(0, 0, 0)
#
#def LedScreen(combined_data):
#    try:
#        myLCD = qwiic_serlcd.QwiicSerlcd()
#
#        if myLCD.connected == False:
#            print("The Qwiic SerLCD device isn't connected to the system. Please check your connection", \
#                file=sys.stderr)
#            return
#
#        myLCD.setBacklight(0, 0, 255) # Set backlight to bright white
#        myLCD.setContrast(1) 
#        myLCD.clearScreen() # clear the screen
#
#        lcdDate = datetime.datetime.now().strftime(' %m/%d, %H:%M')
#        #print(lcdDate)
#        if len(combined_data) > 1:
#            try:
#                co2Float = float(combined_data[1])
#                co2Value = int(co2Float)
#                if co2Value < 1000:
#                    myLCD.setBacklight(0, 255, 0)# bright green
#                elif co2Value > 1000 and  co2Value < 2000:
#                    myLCD.setBacklight(255, 255, 0)# bright yellow
#                elif co2Value > 2000 and  co2Value < 5000:
#                    myLCD.setBacklight(225, 128, 0)# bright Orange
#                elif co2Value > 5000:
#                    myLCD.setBacklight(255, 0, 0)# Red
#
#                data = combined_data[2]
#                temp = (format(int(float(combined_data[3])),'.1f'))
#                humidity = (format(int(float(combined_data[4])),'.1f'))
#
#                myLCD.print( lcdDate)
#                myLCD.setCursor(0,1)
#                myLCD.print(data + " ")
#                myLCD.print(str(temp) + " " + str(humidity))
#            except Exception as e:
#	            print(e)
#    except Exception as e:
#        print(e)
#        myLCD.print( lcdDate)
#        myLCD.setCursor(0,1)
#        myLCD.print("Parsing Error")
#
#
def main():
    #Settings for database connection
    hostname = '192.168.0.33'
    username = 'remote'
    password = 'Bandit2015'
    database = 'Environmental_Data'
    device = 'dev-pi'
    combined_data = []
    co2Data =[]

    mydb = mysql.connector.connect(
      host="hostname",
      user="username",
      password="password",
      database="database"
    )

    mycursor = mydb.cursor()

    mycursor.execute("SELECT * FROM co2_data")

    myresult = mycursor.fetchall()

    for x in myresult:
      print(x)

if __name__=="__main__":
    main()
