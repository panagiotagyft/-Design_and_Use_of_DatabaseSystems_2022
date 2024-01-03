# ----- CONFIGURE YOUR EDITOR TO USE 4 SPACES PER TAB ----- #
import settings
import sys,os
sys.path.append(os.path.join(os.path.split(os.path.abspath(__file__))[0], 'lib'))
import pymysql as db

def connection():
    ''' User this function to create your connections '''
    con = db.connect(
        settings.mysql_host, 
        settings.mysql_user, 
        settings.mysql_passwd, 
        settings.mysql_schema)
    
    return con

def findAirlinebyAge(x,y):
    
    # Create a new connection
    # Create a new connection
    con=connection()
    # Create a cursor on the connection
    cur=con.cursor()

    return [("airline_name","num_of_passengers", "num_of_aircrafts"),]


def findAirportVisitors(x,a,b):
    
   # Create a new connection
    con=connection()
    
    # Create a cursor on the connection
    cur=con.cursor()

    return [("aiport_name", "number_of_visitors"),]

def findFlights(x,a,b):

    # Create a new connection
    con=connection()
    # Create a cursor on the connection
    cur=con.cursor()
    
    
    return [("flight_id", "alt_name", "dest_name", "aircraft_model"),]
    

def findLargestAirlines(N):
    # Create a new connection
    con=connection()

    # Create a cursor on the connection
    cur=con.cursor()
    

    return [("name", "id", "num_of_aircrafts", "num_of_flights"),]
    
def insertNewRoute(x,y):
    # Create a new connection
    con=connection()

    # Create a cursor on the connection
    cur=con.cursor()
    

    return [(),]
