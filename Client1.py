import socket
import time
import inspect
import sys
import datetime
import MySQLdb
import RPi.GPIO as GPIO
from hx711 import HX711


GPIO.cleanup()
GPIO.setwarnings(False)


def cleanAndExit():
    print "Cleaning..."
    GPIO.cleanup()
    print "Bye!"
    sys.exit()

hx = HX711(27, 17)

hx.set_reading_format("LSB", "MSB")
hx.set_reference_unit(-4)
scale=-10000;
# hx711 configuration

def read_weight():
    val = (int)(42.65*(hx.read_average(3)-8055600)/(-1000))
    return val
    

CONSUMER_ID = 2000000000000
RETAILER_ID = 123456789012
host = '127.0.0.1'
port = 5560
use_weight = 0
weight_used = 0
weight_at_recharge = 0

retry_idx = 4
def lineno():
    """Returns the current line number in our program."""
    return inspect.currentframe().f_back.f_lineno

valve_state = 0

relay_pin = 13

for i in range(0, 10):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(relay_pin, GPIO.OUT)
    GPIO.output(relay_pin, GPIO.LOW)
    time.sleep(0.5)



def send_command(iter,current_weight):

#         i = 0
#         weight = i      # function included in weight.py
#         read_time = time.time()
#         read_date = datetime.datetime.fromtimestamp(read_time).strftime('%Y/%m/%d')
#         read_time = datetime.datetime.fromtimestamp(read_time).strftime('%H:%M:%S')
#         command = "SEND " + str(read_date) + " " + str(read_time) + " " + str(weight)
#         print(command)
#         time.sleep(2)
#         i += 1


        # gas = read_gas()
        # valve_state
        # if gas > gas_threshold:
        #   valve_state = 0
        #   print("##....Gas Leak Detected....##")
        #   print("##....Gas Flow Stopped....##")
        #

        print("Iteration : " + str(iter))
        global use_weight
        global weight_at_recharge
        
        i = 0
        weight = current_weight      # function included in weight.py
        read_time = time.time()
        read_date = datetime.datetime.fromtimestamp(read_time).strftime('%Y/%m/%d')
        read_time = datetime.datetime.fromtimestamp(read_time).strftime('%H:%M:%S')
        command = "SEND " + str(CONSUMER_ID) + " " + str(read_date) + " " + str(read_time) + " " + str(weight)
        print(command)
        time.sleep(5)
        i += 1


        host="sql143.main-hosting.eu"
        user="u402156879_lpg1"
        passwd="!prajjwala2k18"
        db="u402156879_lpg1"

        #Connecting to database
        print("\nGot the Credentials")
        try:
            print("Connecting to the Database")
            db = MySQLdb.connect(host, user, passwd, db, connect_timeout = 2 )
            print("##....Connected to the Database....##")
            cur = db.cursor()
            sql_query = "INSERT INTO `CONSUMER_REALTIME_GAS_USAGE`(`CONSUMER_ID`,`DATE`,`TIME`,`GAS_LEFT`) VALUES('%s','%s','%s','%s')" %(CONSUMER_ID, read_date, read_time, weight)
            try:
                print("##....Executing the commit....##")
                cur.execute(sql_query)
                print("##....Commiting the Query....##\n")
                db.commit()
                reply = "Query Executed Succesfully"
            except Exception as e:
                print(e)
                reply = "Error1 " + str(e) + "##....Error Executing the Command....##\n"
                db.rollback()

            if(use_weight == 0 and weight_used <= 0):
                sql_query1 = "SELECT * FROM CONSUMER_GAS_USAGE WHERE CONSUMER_ID = '%i' AND STATUS = '%i'" %(CONSUMER_ID, 1)
                try:
                    cur.execute(sql_query1)
                    results = cur.fetchall()
                    for row in results:
                        print("##....Query Executed....##")
                        print("##....Fetching Data....##")
                        RECHARGE_DATE = row[1]
                        RECHARGE_TIME = row[2]
                        RECHARGE_AMOUNT = row[3]
                        RECHARGE_GAS_EQUIVALENT = row[4]
                        
                        use_weight = RECHARGE_GAS_EQUIVALENT
                        # Now print fetched result
                        print("RECHARGE_DATE='%s'\nRECHARGE_TIME='%s'\nRECHARGE_AMOUNT='%s'\nRECHARGE_GAS_EQUIVALENT='%s'" %(RECHARGE_DATE,RECHARGE_TIME,RECHARGE_AMOUNT,RECHARGE_GAS_EQUIVALENT))

                        update_query = "UPDATE CONSUMER_GAS_USAGE SET STATUS = '%i' WHERE CONSUMER_ID = '%s' AND RECHARGE_TIME = '%s'" %(0,CONSUMER_ID, RECHARGE_TIME)
                        print(update_query)
                        cur.execute(update_query)
                        db.commit()
                        print("\n##....Status Updated....##\n")

                        if(use_weight > 0):
                            weight_at_recharge = read_weight()
                            print("\nSystem Recharged for Rs. " + str(use_weight) + "\n")
                        break;
                except Exception as e:
                        print(e)
                        reply = "Error1 " + str(e) + "##....Error Executing the Command....##\n"
                        db.rollback()
                db.close()
        except Exception as e:
            print(e)
            reply = "Error1 " + str(e) + "We got some Error Connecting to database. Please Try again"

        


        

for i in range(1000):
    # gas = read_gas()
    # valve_state
    # if gas > gas_threshold:
    #   valve_state = 0
    #   print("##....Gas Leak Detected....##")
    #   print("##....Gas Flow Stopped....##")
    # else:


    print("Use Weight : " + str(use_weight) + " g")

    current_weight = read_weight()
    weight_used = weight_at_recharge - current_weight
    if(use_weight > 0 and weight_used < use_weight):
       use_weight = use_weight - weight_used
       #######..........SHUT ON VALVE...........######
       GPIO.output(relay_pin,GPIO.HIGH)
       valve_state = 1:
    if(use_weight > 0 and weight_used <= use_weight):
        use_weight = 0
        #######..........SHUT OFF VALVE...........######
        GPIO.output(relay_pin, GPIO.LOW)
        valve_state = 0:
    if(use_weight == 0):
        #######..........SHUT OFF VALVE...........######
        GPIO.output(relay_pin,GPIO.LOW)
        valve_state = 0:

    #send_command(i)
    send_command(i,current_weight)
    time.sleep(10)
    if valve_state = 0:
        ###    "Switch off Valve" ####
       GPIO.output(relay_pin,GPIO.LOW)
    else:
        ###    "Switch on Valve"  ####
       GPIO.output(relay_pin,GPIO.HIGH)




