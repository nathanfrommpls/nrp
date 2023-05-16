from flask import Flask, render_template, request,redirect
import json
import psycopg2
import datetime

app = Flask(__name__)

@app.route("/")
def index():
    return redirect("/today/", code=302)


@app.route("/today/",methods=['GET', 'POST'])
def today():
    today = datetime.date.today()
    try:
        user_info = quien_es( 1 )
    except Exception as e:
        return render_template("exception.html",exception_string="While getting User Info: " + str(e))
    
    if request.method == 'POST':
        try:
            # ¡Qué boludes! I am certain this is a very hacky way to deal with checkboxes
            # need to research the correct way.
            try:
                exercise = bool(request.form['exercise'])
            except:
                exercise = False
                
            try:
                stretch = bool(request.form['stretch'])
            except:
                stretch = False

            try:    
                sit = bool(request.form['sit'])
            except:
                sit = False

            try:
                sss = bool(request.form['sss'])
            except:
                sss = False

            try:
                journal = bool(request.form['journal'])
            except:
                journal = False

            try:
                vitamins = bool(request.form['vitamins'])
            except:
                vitamins = False

            try:
                brush_am = bool(request.form['brush_am'])
            except:
                brush_am = False

            try:
                brush_pm = bool(request.form['brush_pm'])
            except:
                brush_pm = False

            try:
                floss = bool(request.form['floss'])
            except:
                floss = False

            try:
                water = float(request.form['water'])
            except:
                water = 0.0
                
            update_habits( 1, exercise, stretch, sit, sss, journal, vitamins, brush_am, brush_pm, floss, water )
        except Exception as e:
            return render_template("exception.html",exception_string="While updating habits: " + str(e))
        
        return render_template("dashboard.html",username=user_info['name'],age=calculate_age( user_info['birthdate'] ),height=user_info['height'],sex=iso_5218_sex( user_info['sex'] ),mass=user_info['mass'],systolic=user_info['systolic'],diastolic=user_info['diastolic'],exercise=exercise,stretch=stretch,sit=sit,sss=sss,journal=journal,vitamins=vitamins,brush_am=brush_am,brush_pm=brush_pm,floss=floss,water_drank=water,daily_calories=calories_today(1),target_calories=harris_benedict(calculate_age( user_info['birthdate'] ), user_info['height'], user_info['mass'], user_info['sex'], 1))
    else:
        try:
            habits = current_habits( 1 )
        except Exception as e:
            return render_template("exception.html",exception_string="While getting current habits: " + str(e))
    
        return render_template("dashboard.html",username=user_info['name'],age=calculate_age( user_info['birthdate'] ),height=user_info['height'],sex=iso_5218_sex( user_info['sex'] ),mass=user_info['mass'],systolic=user_info['systolic'],diastolic=user_info['diastolic'],exercise=habits[0],stretch=habits[1],sit=habits[2],sss=habits[3],journal=habits[4],vitamins=habits[5],brush_am=habits[6],brush_pm=habits[7],floss=habits[8],water_drank=habits[9],daily_calories=calories_today(1),target_calories=harris_benedict(calculate_age( user_info['birthdate'] ),  user_info['height'], user_info['mass'], user_info['sex'], 1))



    return render_template("under_construction.html",username=user_info['name'],age=calculate_age( user_info['birthdate'] ),height=user_info['height'],sex=iso_5218_sex( user_info['sex'] ),mass=user_info['mass'],systolic=user_info['systolic'],diastolic=user_info['diastolic'],page_name="User")

@app.route("/food/",methods=['GET', 'POST'])
def food():
    try:
        user_info = quien_es( 1 )
    except Exception as e:
        return render_template("exception.html",exception_string="While getting User Info: " + str(e))
    
    return render_template("food.html",username=user_info['name'],age=calculate_age( user_info['birthdate'] ),height=user_info['height'],sex=iso_5218_sex( user_info['sex'] ),mass=user_info['mass'],systolic=user_info['systolic'],diastolic=user_info['diastolic'],daily_calories=calories_today(1),target_calories=harris_benedict(calculate_age( user_info['birthdate'] ), user_info['height'], user_info['mass'], user_info['sex'], 1),foods=eaten_today(1))

@app.route("/atethissearch/",methods=['GET', 'POST'])
def atethissearch():
    try:
        user_info = quien_es( 1 )
    except Exception as e:
        return render_template("exception.html",exception_string="While getting User Info: " + str(e))
    
    try:
        foods = search_food(request.form['food_description'])
    except Exception as e:
        return render_template("exception.html",exception_string="While search for matching food during ate this: " + str(e))
    
    try:
        return render_template("atethis.html",username=user_info['name'],age=calculate_age( user_info['birthdate'] ),height=user_info['height'],sex=iso_5218_sex( user_info['sex'] ),mass=user_info['mass'],systolic=user_info['systolic'],diastolic=user_info['diastolic'],foods=foods)
    except Exception as e:
        return render_template("exception.html",exception_string="While calling ate this: " + str(e))


@app.route("/atethisthing/",methods=['POST'])
def atethisthing():
    try:
        uid = 1
        fid = request.form['fid']
        quantity = request.form['quantity']
        insert_food_today( uid, fid, quantity )
    except Exception as e:
        return render_template("exception.html",exception_string="While trying insert a record of what was eaten: " + str(e))

    return redirect("/food/", code=302)

@app.route("/atethisnewthing/",methods=['POST'])
def atethisnewthing():
    try:
        uid = 1
        quantity = request.form['quantity']
        precision = request.form['precision']
        description = request.form['description']
        calories = request.form['calories']
        insert_food_db( description, precision, calories )
        foods = search_food(request.form['description'])
        insert_food_today( uid, foods[0][0], quantity )
    except Exception as e:
        return render_template("exception.html",exception_string="While trying insert a record of a new thing that what was eaten: " + str(e))

    return redirect("/food/", code=302)
    
@app.route("/report/",methods=['GET', 'POST'])
def report():
    try:
        user_info = quien_es( 1 )
    except Exception as e:
        return render_template("exception.html",exception_string="While getting User Info: " + str(e))

    return render_template("under_construction.html",username=user_info['name'],age=calculate_age( user_info['birthdate'] ),height=user_info['height'],sex=iso_5218_sex( user_info['sex'] ),mass=user_info['mass'],systolic=user_info['systolic'],diastolic=user_info['diastolic'],page_name="Report")

@app.route("/user/",methods=['GET', 'POST'])
def user():
    try:
        user_info = quien_es( 1 )
    except Exception as e:
        return render_template("exception.html",exception_string="While getting User Info: " + str(e))

    return render_template("under_construction.html",username=user_info['name'],age=calculate_age( user_info['birthdate'] ),height=user_info['height'],sex=iso_5218_sex( user_info['sex'] ),mass=user_info['mass'],systolic=user_info['systolic'],diastolic=user_info['diastolic'],page_name="User")

@app.route("/admin/",methods=['GET', 'POST'])
def admin():
    try:
        user_info = quien_es( 1 )
    except Exception as e:
        return render_template("exception.html",exception_string="While getting User Info: " + str(e))

    return render_template("under_construction.html",username=user_info['name'],age=calculate_age( user_info['birthdate'] ),height=user_info['height'],sex=iso_5218_sex( user_info['sex'] ),mass=user_info['mass'],systolic=user_info['systolic'],diastolic=user_info['diastolic'],page_name="Admin")

# Database
def get_db_conn():
    try:
        with open('dbconn.json', encoding='utf-8') as F:
            json_connection = json.loads(F.read())
    except Exception as e:
        raise e

    try:
        connection = psycopg2.connect(
            host=json_connection['host'],
            database=json_connection['dbname'],
            user=json_connection['username'],
            password=json_connection['password'])
        return connection
    except Exception as e:
        raise e

def quien_es( uid ):
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
    try:
        sql = "SELECT exercise, stretch, sit, sss, journal, vitamins, brush_am, brush_pm, floss, water FROM habits WHERE uid = %s AND date = current_date"
        conn = get_db_conn()
        curs = conn.cursor()
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
    except Exception as e:
        raise e

def update_habits( uid, exercise, stretch, sit, sss, journal, vitamins, brush_am, brush_pm, floss, water ):
    try:
        sql = "INSERT INTO habits ( date, uid, exercise, stretch, sit, sss, journal, vitamins, brush_am, brush_pm, floss, water ) values ( current_date, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s ) ON CONFLICT ( date, uid ) DO UPDATE set exercise = %s, stretch = %s, sit = %s, sss = %s, journal = %s, vitamins = %s, brush_am = %s, brush_pm = %s, floss = %s, water = %s"
        conn = get_db_conn()
        curs = conn.cursor()
        curs.execute(sql, [ uid, exercise, stretch, sit, sss, journal, vitamins, brush_am, brush_pm, floss, water, exercise, stretch, sit, sss, journal, vitamins, brush_am, brush_pm, floss, water ])
        conn.commit()
        curs.close()
        conn.close()
    except Exception as e:
        raise e
    
def iso_5218_sex( sex ):
    if sex == 1:
        return "Male"
    elif sex == 2:
        return "Female"
    else:
        raise Exception("Invalid value received for sex.")

# birthdate must be datetime.date
# Insufficient precision, technical debt.
def calculate_age( birthdate ):
    today = datetime.date.today()
    return  today.year - birthdate.year

# https://en.wikipedia.org/wiki/Harris%E2%80%93Benedict_equation1
# 0: Sedentiary
# 1: Light Exercise
# 2: Moderate Exercise
# 3: Heavy Exercise
# 4: Very Heavy Exercise
def harris_benedict( age, height, weight, sex, activity ):
    activity_multiplier = [ 1.2, 1.375, 1.55, 1.725, 1.9 ]
    if sex == 1:
        sex_modifer = 5
    elif sex == 2:
        sex_modifier = -161
    else:
        raise Exception( sex + " is not a valid iso_5218 value." )
        
    return int(((10 * weight) + ( 6.25 * height ) - ( 5 * age ) +  sex_modifer) * activity_multiplier[activity])

def eaten_today( uid ):
    try:
        sql = "SELECT food.description, eaten_daily.quantity, food.calories * eaten_daily.quantity, food.precision FROM eaten_daily INNER JOIN food ON eaten_daily.fid = food.fid WHERE eaten_daily.uid = %s AND date = current_date;"
        conn = get_db_conn()
        curs = conn.cursor()
        curs.execute(sql,[uid])
        eaten_today = curs.fetchall()
        # Do I need a if eaten_today == None like in the current function?
        return eaten_today
    except Exception as e:
        raise e

def calories_today( uid ):
    try:
        total_daily_calories = 0
        sql = "SELECT eaten_daily.quantity, food.calories FROM eaten_daily INNER JOIN food on eaten_daily.fid = food.fid WHERE eaten_daily.uid = %s AND date = current_date;"
        conn = get_db_conn()
        curs = conn.cursor()
        curs.execute(sql,[uid])
        rows_calories = curs.fetchall()
        for row in rows_calories:
            total_daily_calories = total_daily_calories + row[0] * row[1]
        return total_daily_calories
    except Exception as e:
        raise e

def search_food( description ):
    try:
        sql = "SELECT * FROM food WHERE DESCRIPTION ILIKE %(like)s;" # Why this syntax?
        conn = get_db_conn()
        curs = conn.cursor()
        curs.execute(sql, {'like': '%'+description+'%'})
        food_records = curs.fetchall()
        # Do I need a if eaten_today == None like in the current function?
        return food_records
    except Exception as e:
        raise e

def insert_food_db( description, precision, calories ):
    try:
        # TODO blocked adding to database if it already exists
        sql = "INSERT INTO food ( description, precision, calories ) values ( %s, %s, %s );"
        conn = get_db_conn()
        curs = conn.cursor()
        curs.execute(sql, [description, precision, calories])
        conn.commit()
        curs.close()
        conn.close()
    except Exception as e:
        raise e

def insert_food_today( uid, fid, quantity ):
    try:
        sql = "INSERT INTO eaten_daily ( date, uid, fid, quantity ) values ( current_date, %s, %s, %s );"
        conn = get_db_conn()
        curs = conn.cursor()
        curs.execute(sql, [uid, fid, quantity])
        conn.commit()
        curs.close()
        conn.close()
    except Exception as e:
        raise e
