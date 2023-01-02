from flask import Flask, render_template
import json
import psycopg2
import datetime

app = Flask(__name__)

@app.route("/")
def dashboard():
    try:
        user_info = get_user_info( 1 )
        today = datetime.date.today()
        dob = user_info['birthdate']
        calculated_age = today.year - dob.year
        if user_info['sex'] == 1:
            iso_5218_sex = "Male"
        elif user_info['sex'] == 2:
            iso_5218_sex = "Female"
        else:
            raise Exception("Invalid value received for sex.")
    except Exception as e:
        return render_template("exception.html",exception_string=str(e))

    try:
        habits = current_habits( 1 )
    except Exception as e:
        return render_template("exception.html",exception_string=str(e))
    
    
    #return render_template("dashboard.html",username=user_info['name'],age=calculated_age,height=user_info['height'],sex=iso_5218_sex,mass=user_info['mass'],systolic=user_info['systolic'],diastolic=user_info['diastolic'])
    return render_template("dashboard.html",username=user_info['name'],age=calculated_age,height=user_info['height'],sex=iso_5218_sex,mass=user_info['mass'],systolic=user_info['systolic'],diastolic=user_info['diastolic'],exercise=habits[0],stretch=habits[1],sit=habits[2],sss=habits[3],journal=habits[4],vitamins=habits[5],brush_am=habits[6],brush_pm=habits[7],floss=habits[8],water_drank=habits[9])

# Database
def get_db_conn():
    try:
        with open('dbconn.json', encoding='utf-8') as F:
            json_connection = json.loads(F.read())
    except Exception as e:
        raise e

    try:
        #raise Exception("Does the error change?" + str(json_connection))
        connection = psycopg2.connect(
            host=json_connection['host'],
            database=json_connection['dbname'],
            user=json_connection['username'],
            password=json_connection['password'])
        return connection
    except Exception as e:
        raise e
 
def get_user_info( uid ):
    try:
        conn = get_db_conn()
        sql = "SELECT users.name, users.birthdate, users.height, users.sex, health_metrics.date, health_metrics.mass, health_metrics.systolic, health_metrics.diastolic FROM users INNER JOIN health_metrics ON users.uid = health_metrics.uid WHERE users.uid = %s ORDER BY health_metrics.date DESC LIMIT 1;"
        curs = conn.cursor()
        curs.execute(sql, [uid])
        query_results = curs.fetchone()
        if query_results == None:
            raise Exception("No user info returned from database.")

        user_info = { "name": query_results[0], "birthdate": query_results[1], "height": query_results[2], "sex": query_results[3], "mass": query_results[5], "systolic": query_results[6], "diastolic": query_results[7] }
        curs.close()
        conn.close()
        return user_info
    except Exception as e:
        raise e
    
    
def current_habits( uid ):
    #today = datetime.date.today()
    #sql = "SELECT exercise, stretch, sit, sss, journal, vitamins, brush_am, brush_pm, floss, water FROM habits WHERE uid = %s AND date = %s"
    sql = "SELECT exercise, stretch, sit, sss, journal, vitamins, brush_am, brush_pm, floss, water FROM habits WHERE uid = %s AND date = current_date"
    conn = get_db_conn()
    curs = conn.cursor()
#    curs.execute(sql, [uid,today])
    curs.execute(sql, [uid])
    habit_bools = curs.fetchone()
    if habit_bools == None:
        curs.close()
        conn.close()
        return ( 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.0 )
    else:
        curs.close()
        conn.close()
        return habit_bools
