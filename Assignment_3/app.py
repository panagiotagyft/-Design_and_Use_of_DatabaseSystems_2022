# ----- CONFIGURE YOUR EDITOR TO USE 4 SPACES PER TAB ----- #

#=============================================================================#
#                                                                             #
#                        sdi1900318_sdi2000172_sdi1800199                     # 
#                                                                             #
#=============================================================================#

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
    con=connection()
    # Create a cursor on the connection
    cur=con.cursor()

    sql = ("""select airlines.name, count(distinct relation_2.passengers_id), count(distinct relation_1.airplanes_id)
            from airlines_has_airplanes relation_1, airlines, routes, flights, flights_has_passengers relation_2, passengers
            where
                # Ξεκαθάρισμα άκυρων πλειάδων από το καρτεσιανό γινόμενο των παραπάνω πινάκων
                relation_1.airlines_id = airlines.id and
                airlines.id = routes.airlines_id and
                flights.routes_id = routes.id and
                flights.id = relation_2.flights_id and
                passengers.id = relation_2.passengers_id and
                
                # Με ενδιαφέρουν οι ταξιδιώτες συγκεκριμένων ηλικιών
                ((2022 - passengers.year_of_birth) > '%d') and ((2022 - passengers.year_of_birth) < '%d')
            group by airlines.id
            order by count(distinct relation_2.passengers_id) desc
    """ % (int(y),int(x)))
    cur.execute(sql)
    results = cur.fetchone()
    print(results)

    return [("airline_name","num_of_passengers", "num_of_aircrafts"),(results)]


def findAirportVisitors(x,a,b):
    
   # Create a new connection
    con=connection()
    
    # Create a cursor on the connection
    cur=con.cursor()

    sql = ("""select airp.name, count(p.id)
            from  passengers p, airports airp, flights f, airlines airl 
            where p.id in 
                  ( select fhp.passengers_id
                    from flights_has_passengers fhp
                    where fhp.flights_id=f.id and f.routes_id in
                         ( select r.id
                           from routes r
                           where r.destination_id=airp.id and r.airlines_id=airl.id )
		          ) and airl.name='%s' and f.date>='%s' and f.date <= '%s' 
            group by airp.name
            order by count(p.id) desc
    """ % (str(x),str(a),str(b)))
    
    cur.execute(sql)
    
    results=[]

    results= cur.fetchall()

    for final in results:
        aiport_name=final[0]
        number_of_visitors=final[1]
        print("aiport_name=%s, number_of_visitors=%s" % \
              (aiport_name, number_of_visitors))

    return [("aiport_name", "number_of_visitors"),]+ list(results)

def findFlights(x,a,b):
    
    # Prepare SQL query
    sql=("""select flights.id, airlines.alias, a2.name, airplanes.model
        from airports a1, airports a2, flights, airplanes, airlines, routes
        where routes.airlines_id=airlines.id and routes.id=flights.routes_id and
              routes.source_id=a1.id and routes.destination_id=a2.id and a1.city='%s' and a2.city='%s' and 
              flights.date='%s' and flights.airplanes_id=airplanes.id and
              airlines.active='Y' and airlines.id in 
              ( select aha.airlines_id
                from airlines_has_airplanes aha
                where aha.airplanes_id=airplanes.id
	          )""" % (str(a),str(b),str(x)))
    
    # Create a new connection
    con=connection()
    
    # Create a cursor on the connection
    cur=con.cursor()
    
    # execute SQL query using execute() method.
    cur.execute(sql)
    results = cur.fetchall()

    for final in results:
        flight_id=final[0]
        alt_name=final[1]
        dest_name=final[2]
        aircraft_model=final[3]
        print("flight_id=%d, alt_name=%s, dest_name=%s, aircraft_model=%s" % \
              (flight_id, alt_name, dest_name, aircraft_model))

    return [("flight_id", "alt_name", "dest_name", "aircraft_model"),]+list(results)
    

def findLargestAirlines(N):
    # Create a new connection
    con=connection()

    # Create a cursor on the connection
    cur=con.cursor()

    # Βρίσκουμε το πλήθος αεροπλάνων που έχει η κάθε αεροπορική εταιρεία
    # Ταξινομούμε τις πλειάδες κατά αύξουσα σειρά με βάση το id της αεροπορικής
    sql_1 = """select airlines.name, airlines.code, count(distinct relation.airplanes_id) as 'num_of_aircrafts'
            from airlines, airlines_has_airplanes relation
            where airlines.id = relation.airlines_id 
            group by airlines.id
            order by airlines.id asc"""
    
    cur.execute(sql_1)
    results_1 = cur.fetchall()

    # Βρίσκουμε το πλήθος πτήσεων που έχει η κάθε αεροπορική εταιρεία
    # Ταξινομούμε τις πλειάδες κατά αύξουσα σειρά με βάση το id της αεροπορικής
    sql_2 = """select count(*) as 'num_of_flights'
                from airlines, routes, flights
                where routes.airlines_id = airlines.id and flights.routes_id = routes.id
                group by airlines.id
                order by airlines.id asc"""

    cur.execute(sql_2)
    results_2 = cur.fetchall()

    # Πλήθος αεροπορικών εταιριών
    size = len(results_1)

    # Concatenate results_1 + results_2
    results_all = []
    for i in range(size):
        results_all.append(results_1[i] + results_2[i])

    # Sort results_all by πλήθος_αεροπορικών κατά *φθίνουσα* σειρά
    results_all.sort(key=lambda y: y[3], reverse=True)


    lim = int(N)
    if(int(N) > size):
        lim = size
    
    # Slicing results_all
    final = results_all[:lim] 


    # Λόγω: https://eclass.uoa.gr/modules/forum/viewtopic.php?course=D47&topic=34174&forum=60739
    # Σε περίπτωση ισοβαθμίας της lim-στης πλειάδας με επόμενες της, 
    # το final πρέπει να περιέχει *και* τις επόμενες πλειάδες της lim
    
    index = len(final) - 1
    last_value = final[index][3]
    index += 1

    while(index < size):
        if(results_all[index][3] == last_value):
            final.append(results_all[index])
            index += 1
        else:
            break

    for array in final:
        name=array[0]
        code=array[1]
        num_of_aircrafts=array[2]
        num_of_flights=array[3]
        print("name=%s, code=%s, num_of_aircrafts=%d, num_of_flights=%d" % \
              (name, code, num_of_aircrafts, num_of_flights))


    return [("name", "code", "num_of_aircrafts", "num_of_flights"),] + list(final) 
    
def insertNewRoute(x,y):

    # Create a new connection
    con=connection()

    # Create a cursor on the connection
    cur=con.cursor()
    
    # Από την βάση, βρίσκουμε τις *διαφορετικές* πόλεις, χώρα στις οποίες υπάρχουν αεροδρόμια
    sql_1 = """select distinct airports.city, airports.country
            from airports"""
    cur.execute(sql_1)
    results_1 = cur.fetchall()

    # Βρίσκουμε τις πόλεις, χώρα που πηγαίνει η αεροπορική με alias "x" με αναχώρηση από το αεροδρόμιο με όνομα "y"
    sql_2 = ("""select distinct dest.city, dest.country
            from airlines, routes, airports src, airports dest 
            where
                # Ξεκαθάρισμα άκυρων πλειάδων από το καρτεσιανό γινόμενο των παραπάνω πινάκων
                routes.airlines_id = airlines.id and 
                routes.source_id = src.id and routes.destination_id = dest.id and 

                # Με ενδιαφέρουν μόνο τα δρομολόγια που πραγματοποιεί η αεροπορική με alias "x"
                airlines.alias = '%s' and

                # Με ενδιαφέρουν μόνο τα δρομολόγια που αναχωρούν από το αεροδρόμιο με όνομα "y"
                src.name = '%s'
    """ % (str(x), str(y)))
    
    cur.execute(sql_2)
    results_2 = cur.fetchall()

    # Πάντα θα ισχύει ότι len(results_1) >= len(results_2)
    assert len(results_1) >= len(results_2)

    size_1 = range(len(results_1))
    size_2 = range(len(results_2))

    # results_3 = results_1 - results_2

    results_3 = []
    for i in size_1:
        found = 0;
        for j in size_2:
            if(results_1[i][0] == results_2[j][0] and results_1[i][1] == results_2[j][1]):
                found = 1       # Βρήκα πλειάδα του results_1 αυτούσια στο results_2
                break
        if(found == 0):
            results_3.append(results_1[i])

    assert len(results_3) == (len(results_1) - len(results_2)) 

    if(len(results_3) == 0):     # Το results_3 είναι κενό. Με άλλα λόγια, οι results_1, results_2 ταυτίζονται
        print("airline capacity full")  # Εκτυπώνεται και στον browser αυτό το μήνυμα;
        con.close()
        return [("airline capacity full"),]
    else:
        tuple_1 = results_3[0]          # 1η πλειάδα του results_3
        city = tuple_1[0]
        country = tuple_1[1]

        # Βρίσκουμε τα *διαφορετικά* αεροδρόμια που βρίσκονται στην city, country
        sql_4 =("""select airports.id
                from airports
                where airports.city = '%s' and airports.country = '%s'
        """ % (str(city), str(country)))
        
        cur.execute(sql_4)
        # Επιστρέφει την 1η πλειάδα του πίνακα αποτελέσματος του ερωτήματος sql_4
        # Με άλλα λόγια, επιστρέφει ένα tuple
        tuple = cur.fetchone()
        airport_dest_id = tuple[0]       # id αεροδρομίου που θα εισάγουμε ως αεροδρόμιο προορισμού

        # Θεωρούμε ότι η αεροπορική x υποστηρίζει μόνο ένα αεροδρόμιο με όνομα y
        # Βρίσκουμε το id της αεροπορικής x και το id του αεροδρομίου y
        # Ενδεχομένως να υπάρχουν κι άλλα αεροδρόμια με όνομα y που δεν υποστηρίζει η αεροπορική x,
        # γι' αυτό και συνδυάζουμε τους παρακάτω πίνακες, αντί να κάνουμε ξεχωριστά ερωτήματα για 
        # την αναζήτηση του x.id και y.id
        sql_5 = ("""select distinct airlines.id, src.id
                from airlines, routes, airports src
                where
                    # Ξεκαθάρισμα άκυρων πλειάδων από το καρτεσιανό γινόμενο των παραπάνω πινάκων
                    routes.airlines_id = airlines.id and 
                    routes.source_id = src.id and 

                    # Με ενδιαφέρουν μόνο τα δρομολόγια που πραγματοποιεί η αεροπορική με alias "x"
                    airlines.alias = '%s' and

                    # Με ενδιαφέρουν μόνο τα δρομολόγια που αναχωρούν από το αεροδρόμιο με όνομα "y"
                    src.name = '%s'
        """ % (str(x), str(y)))

        cur.execute(sql_5)
        tuple = cur.fetchone()
        airline_id = tuple[0]           # id αεροπορικής x
        airport_src_id = tuple[1]       # id αεροδρομίου y 


        # Βρίσκουμε το routes_id προς προσθήκη
        sql_6 = """select routes.id
                from routes
                order by routes.id desc"""
        cur.execute(sql_6)
        tuple = cur.fetchone()
        routes_id = tuple[0]             
        routes_id += 1              # routes_id to be inserted

        sql_7 = ("""insert into routes(id, airlines_id, source_id, destination_id)
                values ('%d', '%d', '%d', '%d')""" % (int(routes_id), int(airline_id), int(airport_src_id), int(airport_dest_id)))
        

        try:
            cur.execute(sql_7)
            con.commit()
            print("OK")
            con.close()
            return [("OK"),]
        except:
            # Rollback in case there is any error
            con.rollback()
            print("Εrror")
            con.close()
            return [("Error"),]
