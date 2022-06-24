#
#
# This project will collect temperature,  humidity, and CO2  information using a SCD30 sensor
# and send this information to a MySQL database.
#
from __future__ import print_function
import time
import sys
import time
import board
import busio
import adafruit_scd30
import datetime
import mysql.connector
from digitalio import DigitalInOut, Direction, Pull
from adafruit_pm25.i2c import PM25_I2C
import serial
import adafruit_bme680

#mydict = {'user': 'Bot', 'version': 0.15, 'items': 43, 'methods': 'standard', 'time': 1536304833437, 'logs': 'no', 'status': 'completed'}

#columns = ', '.join("`" + str(x).replace('/', '_') + "`" for x in mydict.keys())
#values = ', '.join("'" + str(x).replace('/', '_') + "'" for x in mydict.values())
#sql = "INSERT INTO %s ( %s ) VALUES ( %s );" % ('mytable', columns, values)
#print(sql)


def particleSensor():
    reset_pin = None
    i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)
    pm25 = PM25_I2C(i2c, reset_pin)
   #print("Found PM2.5 sensor, reading data...")

    try:
        aqdata = pm25.read()
        # print(aqdata)
    except RuntimeError:
        print("Unable to read from sensor, retrying...")
    particledata = {}
    pm10 = aqdata["pm10 standard"]
    pm25 = aqdata["pm25 standard"]
    pm100 = aqdata["pm100 standard"]
    particledata = {"PM10":pm10,"PM2.5": pm25,"PM100": pm100}
    return particledata
 
    #print()
    #print("Concentration Units (standard)")
    #print("---------------------------------------")
    #print(
    #        "PM 1.0: %d\tPM2.5: %d\tPM10: %d"
    #         % (aqdata["pm10 standard"], aqdata["pm25 standard"], aqdata["pm100 standard"])
    #    )
    #print("Concentration Units (environmental)")
    #print("---------------------------------------")
    #print(
    #    "PM 1.0: %d\tPM2.5: %d\tPM10: %d"
    #    % (aqdata["pm10 env"], aqdata["pm25 env"], aqdata["pm100 env"])
    #    )
    #print("---------------------------------------")
    #print("Particles > 0.3um / 0.1L air:", aqdata["particles 03um"])
    #print("Particles > 0.5um / 0.1L air:", aqdata["particles 05um"])
    #print("Particles > 1.0um / 0.1L air:", aqdata["particles 10um"])
    #print("Particles > 2.5um / 0.1L air:", aqdata["particles 25um"])
    #print("Particles > 5.0um / 0.1L air:", aqdata["particles 50um"])
    #print("Particles > 10 um / 0.1L air:", aqdata["particles 100um"])
    #print("---------------------------------------")



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
            print("Error with db insert")




def bme680():
    bme_data = {}
    try:
        i2ca = board.I2C() 
        bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2ca, debug=False)

        try:
            bmetemp = bme680.temperature * 9/5.0 + 32
            bmehumidity = bme680.relative_humidity
            bmegas = bme680.gas
            bmepressure = bme680.pressure
            bmealtitude = bme680.altitude

            bme_data ={"bme temp": format(bmetemp,'.2f'),"bme humidity":format(bmehumidity,'.1f'),"bme gas": bmegas,"bme Pressure":format(bmepressure, '.2f'),"bme altitude": format(bmealtitude, '.2f')}
            #print(bme_data)
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)
    return bme_data

def main():
    # Main loop

    try:
        i2c = busio.I2C(board.SCL, board.SDA)
        scd = adafruit_scd30.SCD30(i2c)

        try:
            try:
                data = scd.data_available
            except RuntimeError:
                print("Unable to read from CO2 sensor, retrying...")
            if data:
                #print("Data Available!")
                co2_Data ={}
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
            try:
                insert_record(device,str(date),format(temp,'.2f'),format(humidity,'.2f'), format(co2,'.2f'), co2_rating)
                #print (device,str(date),format(temp,'.2f'),format(humidity,'.2f'), format(co2,'.2f'), co2_rating)
            except:
                pass

            co2_Data ={"scd30 temp": format(temp,'.2f'),"CO2":format(co2,'.2f'),"CO2 rating": co2_rating}
            #print(co2_Data)
        except:
            print("error 1")
    except:
        print("Error 2")
    return co2_Data


if __name__=="__main__":

    #Settings for database connection
    hostname = '192.168.0.32'
    username = 'remote'
    password = 'Bandit2015'
    database = 'eniv_data'
    device = 'dev-pi'

    now = datetime.datetime.now()
    date = now.strftime('%Y-%m-%d %H:%M:%S')

    combined_data = {}
    default ={"device": device, "dt": date}
    co2Data ={}
    try:
        co2Data = main()

        try:
            combined_data = default | co2Data
        except Exception as e:
            print(e)

    except Exception as e:
        print(e)
    try:
        bme_data = bme680()
        try:
            combined_data = combined_data | bme_data
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)
    try:
        particle_data = particleSensor()
        try:
           combined_data = dict(list(combined_data.items()) + list(particle_data.items()))
        except Exception as e:
            print(e)
    except Exception as e:
        print(e)

    print(combined_data)
