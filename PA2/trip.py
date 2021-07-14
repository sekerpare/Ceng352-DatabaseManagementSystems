import datetime

from user import User

import psycopg2

from config import read_config
from messages import *

POSTGRESQL_CONFIG_FILE_NAME = "database.cfg"

sign_in_time=0

"""
    Connects to PostgreSQL database and returns connection object.
"""


def connect_to_db():
    db_conn_params = read_config(filename=POSTGRESQL_CONFIG_FILE_NAME, section="postgresql")
    conn = psycopg2.connect(**db_conn_params)
    conn.autocommit = False
    return conn


"""
    Splits given command string by spaces and trims each token.
    Returns token list.
"""


def tokenize_command(command):
    tokens = command.split(" ")
    return [t.strip() for t in tokens]


"""
    Prints list of available commands of the software.
"""


def help(conn, user):
    # TODO: Create behaviour of the application for different type of users: Non Authorized (not signed id), Free and Premium users.


    IS_PREM ="SELECT * " \
             "FROM Subscription S " \
             "WHERE S.user_id = %s ;"

    if user:
        try:
            cur = conn.cursor()
            cur.execute(IS_PREM, (str(user.user_id),))
            isprem = cur.fetchone()
            if isprem:
                print("\n*** Please enter one of the following commands ***")
                print("> help")
                print("> sign_up <user_id> <first_name> <last_name>")
                print("> sign_in <user_id>")
                print("> sign_out")
                print("> show_memberships")
                print("> show_subscription")
                print("> subscribe <membership_id>")
                print("> review <review_id> <business_id> <stars>")
                print("> search_for_businesses <keyword_1> <keyword_2> <keyword_3> ... <keyword_n>")
                print("> suggest_businesses")
                print("> get_coupon")
                print("> quit")
            else:
                print("\n*** Please enter one of the following commands ***")
                print("> help")
                print("> sign_up <user_id> <first_name> <last_name>")
                print("> sign_in <user_id>")
                print("> sign_out")
                print("> show_memberships")
                print("> show_subscription")
                print("> subscribe <membership_id>")
                print("> review <review_id> <business_id> <stars>")
                print("> search_for_businesses <keyword_1> <keyword_2> <keyword_3> ... <keyword_n>")
                print("> quit")
        except (Exception, psycopg2.DatabaseError):
            conn.rollback()
            conn.close()
            return None, USER_SIGNIN_FAILED
    else:
        print("\n*** Please enter one of the following commands ***")
        print("> help")
        print("> sign_up <user_id> <first_name> <last_name>")
        print("> sign_in <user_id>")
        print("> quit")


"""
    Saves user with given details.
    - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
    - If the operation is successful, commit changes and return tuple (True, CMD_EXECUTION_SUCCESS).
    - If any exception occurs; rollback, do nothing on the database and return tuple (False, CMD_EXECUTION_FAILED).
"""



def sign_up(conn, user_id, user_name):
    # TODO: Implement this function
    statement = "INSERT INTO Users(user_id, user_name, review_count, yelping_since, useful, funny, cool, fans, average_stars, session_count) " \
                "VALUES(%s,%s,0,(SELECT CURRENT_TIMESTAMP),0,0,0,0,0,0) ;"
    try:
        cur = conn.cursor()
        cur.execute(statement,(str(user_id),str(user_name)))
        conn.commit()
        cur.close()
        return True, CMD_EXECUTION_SUCCESS
    except (Exception, psycopg2.DatabaseError):
        conn.rollback()
        conn.close()
        return False, CMD_EXECUTION_FAILED


"""
    Retrieves user information if there is a user with given user_id and user's session_count < max_parallel_sessions.
    - Return type is a tuple, 1st element is a user object and 2nd element is the response message from messages.py.
    - If there is no such user, return tuple (None, USER_SIGNIN_FAILED).
    - If session_count < max_parallel_sessions, commit changes (increment session_count) and return tuple (user, CMD_EXECUTION_SUCCESS).
    - If session_count >= max_parallel_sessions, return tuple (None, USER_ALL_SESSIONS_ARE_USED).
    - If any exception occurs; rollback, do nothing on the database and return tuple (None, USER_SIGNIN_FAILED).
"""


def sign_in(conn, user_id):
    SELECT_USER = "SELECT * " \
                  "FROM Users U " \
                  "WHERE user_id = %s ;"

    SELECT_MAX  = "SELECT M.max_parallel_sessions " \
                  "FROM Subscription S, Membership M " \
                  "WHERE S.membership_id = M.membership_id " \
                  "  AND S.user_id = %s ;"

    UPDATE_USER = "UPDATE Users " \
                  "SET session_count=session_count+1 " \
                  "WHERE user_id = %s ;"

    try:
        cur = conn.cursor()
        cur.execute(SELECT_USER,(str(user_id),))
        user_tuple = cur.fetchone()
        cur.execute(SELECT_MAX, (str(user_id),))
        max_parallel_sessions = cur.fetchone()
        if (max_parallel_sessions==None and user_tuple[9]==0):
            cur.execute(UPDATE_USER, (str(user_id),))
            user = User(user_tuple[0], user_tuple[1], user_tuple[2], user_tuple[3],
                        user_tuple[4], user_tuple[5], user_tuple[6], user_tuple[7],
                        user_tuple[8], user_tuple[9] + 1)

            conn.commit()
            cur.close()
            return user, CMD_EXECUTION_SUCCESS
        elif (max_parallel_sessions and user_tuple[9] < max_parallel_sessions[0]):
            cur.execute(UPDATE_USER, (str(user_id),))
            user = User(user_tuple[0],user_tuple[1],user_tuple[2],user_tuple[3],
                        user_tuple[4],user_tuple[5],user_tuple[6],user_tuple[7],
                        user_tuple[8],user_tuple[9]+1)
            global sign_in_time
            sign_in_time = datetime.datetime.now()
            conn.commit()
            cur.close()
            return user, CMD_EXECUTION_SUCCESS
        else:
            conn.commit()
            cur.close()
            return None, USER_ALL_SESSIONS_ARE_USED
    except (Exception, psycopg2.DatabaseError):
        conn.rollback()
        conn.close()
        return None, USER_SIGNIN_FAILED


"""
    Signs out from given user's account.
    - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
    - Decrement session_count of the user in the database.
    - If the operation is successful, commit changes and return tuple (True, CMD_EXECUTION_SUCCESS).
    - If any exception occurs; rollback, do nothing on the database and return tuple (False, CMD_EXECUTION_FAILED).
"""


def sign_out(conn, user):
    # TODO: Implement this function
    IS_PREM =  "SELECT * " \
               "FROM Subscription " \
               "WHERE user_id = %s ;"
    UPDATE_USER = "UPDATE Users " \
                  "SET session_count=session_count-1 " \
                  "WHERE user_id = %s;"

    UPDATE_TIME = "UPDATE Subscription " \
                  "SET time_spent= %s " \
                  "WHERE user_id = %s;"
    try:
        cur = conn.cursor()
        cur.execute(UPDATE_USER,(str(user.user_id),))
        cur.execute(IS_PREM, (str(user.user_id),))
        isprem = cur.fetchone()
        if isprem:
            now=datetime.datetime.now()
            difference=now-sign_in_time
            ms=difference.total_seconds()*1000
            cur.execute(UPDATE_TIME, (str(ms),str(user.user_id)))
        conn.commit()
        cur.close()
        return True, CMD_EXECUTION_SUCCESS
    except (Exception, psycopg2.DatabaseError):
        conn.rollback()
        conn.close()
        return False, CMD_EXECUTION_FAILED


"""
    Quits from program.
    - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
    - Remember to sign authenticated user out first.
    - If the operation is successful, commit changes and return tuple (True, CMD_EXECUTION_SUCCESS).
    - If any exception occurs; rollback, do nothing on the database and return tuple (False, CMD_EXECUTION_FAILED).
"""


def quit(conn, user):
    # TODO: Implement this function
    try:
        if user :
            sign_out(conn, user)
        return True, CMD_EXECUTION_SUCCESS
    except (Exception, psycopg2.DatabaseError):
        conn.rollback()
        conn.close()
        return False, CMD_EXECUTION_FAILED


"""
    Retrieves all available memberships and prints them.
    - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
    - If the operation is successful; print available memberships and return tuple (True, CMD_EXECUTION_SUCCESS).
    - If any exception occurs; return tuple (False, CMD_EXECUTION_FAILED).

    Output should be like:
    #|Name|Max Sessions|Monthly Fee
    1|Silver|2|30
    2|Gold|4|50
    3|Platinum|10|90
"""


def show_memberships(conn,user):
    # TODO: Implement this function
    SELECT_MEM = "SELECT *" \
                 "FROM Membership M ;"
    try:
        cur = conn.cursor()
        cur.execute(SELECT_MEM)
        mem_list = cur.fetchall()
        print("#|Name|Max Sessions|Monthly Fee")
        for mem in mem_list :
            print(str(mem[0])+"|"+str(mem[1])+"|"+str(mem[2])+"|"+str(mem[3]))
        conn.commit()
        cur.close()
        return True, CMD_EXECUTION_SUCCESS
    except (Exception, psycopg2.DatabaseError):
        conn.rollback()
        conn.close()
        return False, CMD_EXECUTION_FAILED


"""
    Retrieves authenticated user's membership and prints it. 
    - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
    - If the operation is successful; print the authenticated user's membership and return tuple (True, CMD_EXECUTION_SUCCESS).
    - If any exception occurs; return tuple (False, CMD_EXECUTION_FAILED).

    Output should be like:
    #|Name|Max Sessions|Monthly Fee
    2|Gold|4|50
"""


def show_subscription(conn, user):
    # TODO: Implement this function
    SELECT_SUB = "SELECT M.membership_id, M.membership_name ,M.max_parallel_sessions, M.monthly_fee " \
                 "FROM Subscription S, Membership M " \
                 "WHERE S.membership_id = M.membership_id " \
                 "  AND S.user_id = %s;"
    try:
        cur = conn.cursor()
        cur.execute(SELECT_SUB,(str(user.user_id),))
        mem_list = cur.fetchall()
        print("#|Name|Max Sessions|Monthly Fee")
        for mem in mem_list:
            print(str(mem[0]) + "|" + str(mem[1]) + "|" + str(mem[2]) + "|" + str(mem[3]))
        conn.commit()
        cur.close()
        return True, CMD_EXECUTION_SUCCESS
    except (Exception, psycopg2.DatabaseError):
        conn.rollback()
        conn.close()
        return False, CMD_EXECUTION_FAILED

"""
    Insert user-review-business relationship to Review table if not exists in Review table.
    - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
    - If a user-review-business relationship already exists (checking review_id is enough), do nothing on the database and return (True, CMD_EXECUTION_SUCCESS).
    - If the operation is successful, commit changes and return tuple (True, CMD_EXECUTION_SUCCESS).
    - If the business_id is incorrect; rollback, do nothing on the database and return tuple (False, CMD_EXECUTION_FAILED).
    - If any exception occurs; rollback, do nothing on the database and return tuple (False, CMD_EXECUTION_FAILED).
"""


def review(conn, user, review_id, business_id, stars):
    # TODO: Implement this function
    IS_REV = "SELECT * " \
             "FROM Review R " \
             "WHERE R.review_id= %s ;"

    IS_BUS = "SELECT * " \
             "FROM Business B " \
             "WHERE B.business_id= %s ;"

    INSERT_REV = "INSERT INTO Review(review_id, user_id, business_id, stars, date, useful, funny, cool) " \
                 "VALUES(%s,%s,%s,%s,(SELECT CURRENT_TIMESTAMP),0,0,0);"

    try:
        cur = conn.cursor()
        cur.execute(IS_REV, (str(review_id),))
        rev_id = cur.fetchone()
        cur.execute(IS_BUS, (str(business_id),))
        bus_id = cur.fetchone()
        if rev_id or bus_id==None :
            conn.commit()
            cur.close()
            return False, CMD_EXECUTION_FAILED
        else :
            cur.execute(INSERT_REV, (str(review_id),str(user.user_id),str(business_id),str(stars)))
            cur.close()
            return True, CMD_EXECUTION_SUCCESS
    except (Exception, psycopg2.DatabaseError) as error:
        conn.rollback()
        conn.close()
        return False, CMD_EXECUTION_FAILED


"""
    Subscribe authenticated user to new membership.
    - Return type is a tuple, 1st element is a user object and 2nd element is the response message from messages.py.
    + If target membership does not exist on the database, return tuple (None, SUBSCRIBE_MEMBERSHIP_NOT_FOUND).
    + If the new membership's max_parallel_sessions < current membership's max_parallel_sessions, return tuple (None, SUBSCRIBE_MAX_PARALLEL_SESSIONS_UNAVAILABLE).
    + If the operation is successful, commit changes and return tuple (user, CMD_EXECUTION_SUCCESS).
    + If any exception occurs; rollback, do nothing on the database and return tuple (None, CMD_EXECUTION_FAILED).
"""


def subscribe(conn, user, membership_id):
    # TODO: Implement this function
    IS_MEM_ID  = "SELECT M.membership_id " \
                 "FROM Membership M " \
                 "WHERE M.membership_id = %s ;"

    INSERT_SUB = "INSERT INTO Subscription(user_id,membership_id, time_spent)" \
                 "VALUES(%s,%s,0) ;"

    UPDATE_SUB = "UPDATE Subscription " \
                 "SET membership_id= %s " \
                 "WHERE user_id = %s;"

    MAX_CURRENT = "SELECT M.max_parallel_sessions " \
                  "FROM Subscription S, Membership M " \
                  "WHERE S.membership_id = M.membership_id " \
                  "  AND S.user_id = %s;"

    MAX_NEW     = "SELECT M.max_parallel_sessions " \
                  "FROM Membership M " \
                  "WHERE M.membership_id = %s;"

    try:
        cur = conn.cursor()
        cur.execute(IS_MEM_ID, (str(membership_id),))
        mem_id = cur.fetchone()
        if mem_id :
            cur.execute(MAX_CURRENT, (str(user.user_id),))
            max_current = cur.fetchone()
            if max_current :
                max_current=max_current[0]
                cur.execute(MAX_NEW, (str(membership_id),))
                max_new = cur.fetchone()[0]
                if max_current<= max_new :
                    cur.execute(UPDATE_SUB ,(str(membership_id),str(user.user_id)))
                    conn.commit()
                    cur.close()
                    return user, CMD_EXECUTION_SUCCESS
                else:
                    conn.commit()
                    cur.close()
                    return None, SUBSCRIBE_MAX_PARALLEL_SESSIONS_UNAVAILABLE
            else:
                cur.execute(INSERT_SUB ,(str(user.user_id),str(membership_id)) )
                conn.commit()
                cur.close()
                return user, CMD_EXECUTION_SUCCESS
        else:
            conn.commit()
            cur.close()
            return None, SUBSCRIBE_MEMBERSHIP_NOT_FOUND
    except (Exception, psycopg2.DatabaseError) :
        conn.rollback()
        conn.close()
        return None, CMD_EXECUTION_FAILED

"""
    Searches for businesses with given search_text.
    - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.
    - Print all businesses whose names contain given search_text IN CASE-INSENSITIVE MANNER.
    - If the operation is successful; print businesses found and return tuple (True, CMD_EXECUTION_SUCCESS).
    - If any exception occurs; return tuple (False, CMD_EXECUTION_FAILED).

    Output should be like:
    Id|Name|State|Is_open|Stars
    1|A4 Coffee Ankara|ANK|1|4
    2|Tetra N Caffeine Coffee Ankara|ANK|1|4
    3|Grano Coffee Ankara|ANK|1|5
"""


def search_for_businesses(conn, user, search_text):
    # TODO: Implement this function
    SEARCH  = "SELECT * " \
              "FROM Business B " \
              "WHERE B.business_name LIKE %s " \
              "ORDER BY B.business_id ;"

    try:
        cur = conn.cursor()
        cur.execute(SEARCH,("%"+str(search_text)+"%",))
        bus_list= cur.fetchall()
        print("Id|Name|State|Is_open|Stars")
        if bus_list:
            for bus in bus_list:
                print(str(bus[0]) + "|" + str(bus[1]) + "|" + str(bus[2]) + "|" + str(bus[3])+ "|" + str(bus[4]))
        conn.commit()
        cur.close()
        return True, CMD_EXECUTION_SUCCESS
    except (Exception, psycopg2.DatabaseError):
        conn.rollback()
        conn.close()
        return False, CMD_EXECUTION_FAILED


"""
    Suggests combination of these businesses:

        1- Gather the reviews of that user.  From these reviews, find the top state by the reviewed business count.  
        Then, from all open businesses find the businesses that is located in the found state.  
        You should collect top 5 businesses by stars.

        2- Perform the same thing on the Tip table instead of Review table.

        3- Again check the review table to find the businesses get top stars from that user.  
        Among them get the latest reviewed one.  Now you need to find open top 3 businesses that is located in the same state 
        and has the most stars (if there is an equality order by name and get top 3).


    - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.    
    - Output format and return format are same with search_for_businesses.
    - Order these businesses by their business_id, in ascending order at the end.
    - If the operation is successful; print businesses suggested and return tuple (True, CMD_EXECUTION_SUCCESS).
    - If any exception occurs; return tuple (False, CMD_EXECUTION_FAILED).
"""


def suggest_businesses(conn, user):
    # TODO: Implement this function

    IS_PREM = "SELECT * " \
              "FROM Subscription S " \
              "WHERE S.user_id = %s ;"

    SUGGEST = "SELECT DISTINCT * " \
              "FROM  Business B_all " \
              "WHERE B_all.business_id IN (SELECT B1.business_id " \
                                          "FROM Business B1 " \
                                          "WHERE B1.state = ( SELECT B1_in.state " \
                                                             "FROM Review R , Business B1_in " \
                                                             "WHERE R.user_id= %s " \
                                                             "AND R.business_id=B1_in.business_id " \
                                                             "GROUP BY B1_in.state " \
                                                             "ORDER BY Count(*) DESC " \
                                                             "LIMIT 1) " \
                                          "AND B1.is_open " \
                                          "ORDER BY B1.stars DESC " \
                                          "LIMIT 5) " \
              "OR B_all.business_id IN (SELECT B2.business_id " \
                                       "FROM Business B2 " \
                                       "WHERE B2.state = ( SELECT B2_in.state " \
                                                          "FROM Tip T , Business B2_in " \
                                                          "WHERE T.user_id= %s " \
                                                          "AND T.business_id=B2_in.business_id " \
                                                          "GROUP BY B2_in.state " \
                                                          "ORDER BY Count(*) DESC " \
                                                          "LIMIT 1) " \
                                        "AND B2.is_open " \
                                        "ORDER BY B2.stars DESC " \
                                       "LIMIT 5) " \
              "OR B_all.business_id IN (SELECT B3.business_id  " \
                                       "FROM Business B3 " \
                                       "WHERE B3.state = ( SELECT B3_in.state " \
                                                          "FROM Review R , Business B3_in " \
                                                          "WHERE R.user_id = %s " \
                                                          "AND R.business_id=B3_in.business_id " \
                                                          "ORDER BY B3_in.stars DESC , R.date DESC " \
                                                          "LIMIT 1) " \
                                        "AND B3.is_open " \
                                        "ORDER BY B3.stars DESC, B3.business_name DESC " \
                                       "LIMIT 3) " \
              "ORDER BY B_all.business_id ; "

    try:
        cur = conn.cursor()
        cur.execute(IS_PREM, (str(user.user_id),))
        isprem = cur.fetchone()
        if isprem:
            cur.execute(SUGGEST, (str(user.user_id),str(user.user_id),str(user.user_id)))
            bus_list = cur.fetchall()
            print("Id|Name|State|Is_open|Stars")
            for bus in bus_list:
                print(str(bus[0]) + "|" + str(bus[1]) + "|" + str(bus[3]) + "|" + str(bus[4]) + "|" + str(bus[5]))
            conn.commit()
            cur.close()
            return True, CMD_EXECUTION_SUCCESS
        else:
            return False, NOT_ALLOWED
    except (Exception, psycopg2.DatabaseError) :
        conn.rollback()
        conn.close()
        return False, CMD_EXECUTION_FAILED


"""
    Create coupons for given user. Coupons should be created by following these steps:

        1- Calculate the score by using the following formula:
            Score = timespent + 10 * reviewcount

        2- Calculate discount percentage using the following formula (threshold given in messages.py):
            actual_discount_perc = score/threshold * 100

        3- If found percentage in step 2 is lower than 25% print the following:
            You don’t have enough score for coupons.

        4- Else if found percentage in step 2 is between 25-50% print the following:
            Creating X% discount coupon.

        5- Else create 50% coupon and remove extra time from user's time_spent:
            Creating 50% discount coupon.

    - Return type is a tuple, 1st element is a boolean and 2nd element is the response message from messages.py.    
    - If the operation is successful (step 4 or 5); return tuple (True, CMD_EXECUTION_SUCCESS).
    - If the operation is not successful (step 3); return tuple (False, CMD_EXECUTION_FAILED).
    - If any exception occurs; return tuple (False, CMD_EXECUTION_FAILED).


"""

def get_coupon(conn, user):
    # TODO: Implement this function
    IS_PREM = "SELECT * " \
              "FROM Subscription S " \
              "WHERE S.user_id = %s ;"

    SELECT_SCORE = "SELECT U.review_count, S.time_spent " \
                   "FROM  Subscription S, Users U " \
                   "WHERE S.user_id = U.user_id " \
                   "  AND S.user_id = %s;"

    UPDATE_TIME = "UPDATE Subscription " \
                  "SET time_spent= %s " \
                  "WHERE user_id = %s ;"

    try:
        cur = conn.cursor()
        cur.execute(IS_PREM, (str(user.user_id),))
        isprem = cur.fetchone()
        if isprem:
            cur.execute(SELECT_SCORE, (str(user.user_id),))
            select = cur.fetchone()
            reviewcount=select[0]
            timespent  =select[1]
            score= timespent + 10 * reviewcount
            actual_discount_perc = score / threshold * 100
            if  actual_discount_perc <25:
                print("You don’t have enough score for coupons.")
            elif actual_discount_perc >=25 and actual_discount_perc <=50 :
                print("Creating "+str(actual_discount_perc)+"% discount coupon.")
                cur.execute(UPDATE_TIME, (str(user.user_id),str(0)))
            else :
                print("Creating 50% discount coupon.")
                newtime=timespent-(threshold/2)
                cur.execute(UPDATE_TIME, ( str(newtime),str(user.user_id)))
            conn.commit()
            cur.close()
            return True, CMD_EXECUTION_SUCCESS
        else:
            return False, NOT_ALLOWED
    except (Exception, psycopg2.DatabaseError):
        conn.rollback()
        conn.close()
        return False, CMD_EXECUTION_FAILED
