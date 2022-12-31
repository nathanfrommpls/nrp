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
    
    return render_template("dashboard.html",username=user_info['name'],age=calculated_age,height=user_info['height'],sex=iso_5218_sex,mass=user_info['mass'],systolic=user_info['systolic'],diastolic=user_info['diastolic'])

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
        sql = "SELECT users.name, users.birthdate, users.height, users.sex, health_metrics.date, health_metrics.mass, health_metrics.systolic, health_metrics.diastolic FROM users INNER JOIN health_metrics ON users.uid = health_metrics.uid WHERE users.uid = '1' ORDER BY health_metrics.date DESC LIMIT 1;"
        cur = conn.cursor()
        cur.execute(sql)
        query_results = cur.fetchone()

        if query_results == None:
            raise Exception("No user info returned from database.")

        user_info = { "name": query_results[0], "birthdate": query_results[1], "height": query_results[2], "sex": query_results[3], "mass": query_results[4], "systolic": query_results[5], "diastolic": query_results[6] }
        cur.close()
        conn.close()
        return user_info
    except Exception as e:
        raise e
    
    
