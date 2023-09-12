from flask import Flask, render_template, request,redirect
import flask_login
# from werkzeug.middleware.proxy_fix import ProxyFix # Uncomment when deployed to production, i.e. nginx and gunicorn
import json
import psycopg2
import datetime
import hashlib

# Production deployment requires instantiating the app wit ProxyFix
app = Flask(__name__)

# app.wsgi_app = ProxyFix( # Uncomment when deployed to production, i.e. nginx and gunicorn
#    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
# )

app.secret_key = 'changeme'
login_manager = flask_login.LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    try:
        return User(user_id)
    except Exception as e:
        return None

@login_manager.unauthorized_handler
def unauthorized_handler():
    return render_template("unauthorized.html")
    #return 'Unauthorized', 401
    
@app.route("/")
@flask_login.login_required
def index():
    return redirect("/newtoday/", code=303)

@app.route("/newtoday/",methods=['GET', 'POST'])
@flask_login.login_required
def newtoday():
    today = datetime.date.today()
    try:
        #me = User(1)
        # What other considerations are there with use the flask_login user?
        # A method to data from database? Maybe on changes on page load?
        me = flask_login.current_user
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
                
            update_habits( me.uid, exercise, stretch, sit, sss, journal, vitamins, brush_am, brush_pm, floss, water, me.timezone )
        except Exception as e:
            return render_template(
                "exception.html",
                exception_string="While updating habits: " + str(e)
            )
        
        return render_template(
           "today.html",
           user=me,
           exercise=exercise,
           stretch=stretch,
           sit=sit,
           sss=sss,
           journal=journal,
           vitamins=vitamins,
           brush_am=brush_am,
           brush_pm=brush_pm,
           floss=floss,
           water_drank=water,
           daily_calories=calories_today(me.uid, me.timezone),
           foods=eaten_today(me.uid, me.timezone)
       )
    else:
        try:
            habits = current_habits( me.uid, me.timezone )
        except Exception as e:
            return render_template(
                "exception.html",
                exception_string="While getting current habits: " + str(e)
            )
    
        return render_template(
           "today.html",
           user=me,
           exercise=habits[0],
           stretch=habits[1],
           sit=habits[2],
           sss=habits[3],
           journal=habits[4],
           vitamins=habits[5],
           brush_am=habits[6],
           brush_pm=habits[7],
           floss=habits[8],
           water_drank=habits[9],
           daily_calories=calories_today(me.uid, me.timezone),
           foods=eaten_today(me.uid, me.timezone)
       )

#    return render_template("under_construction.html",username=user_info['name'],age=calculate_age( user_info['birthdate'] ),height=user_info['height'],sex=iso_5218_sex( user_info['sex'] ),mass=user_info['mass'],systolic=user_info['systolic'],diastolic=user_info['diastolic'],page_name="User",timezone=user_info['timezone'])

@app.route("/food/",methods=['GET', 'POST'])
@flask_login.login_required
def food():
    try:
        user_info = quien_es( 1 )
    except Exception as e:
        return render_template(
            "exception.html",
            exception_string="While getting User Info: " + str(e)
        )
    
    return render_template(
        "food.html",
        username=user_info['name'],
        age=calculate_age( user_info['birthdate'] ),
        height=user_info['height'],
        sex=iso_5218_sex( user_info['sex'] ),
        mass=user_info['mass'],
        systolic=user_info['systolic'],
        diastolic=user_info['diastolic'],
        daily_calories=calories_today(1, user_info['timezone']),
        target_calories=harris_benedict(calculate_age( user_info['birthdate'] ),user_info['height'], user_info['mass'], user_info['sex'], 1),foods=eaten_today(1, user_info['timezone']),
        timezone=user_info['timezone']
    )

@app.route("/atethissearch/",methods=['GET', 'POST'])
@flask_login.login_required
def atethissearch():
    try:
        #me = User(1)
        me = flask_login.current_user
    except Exception as e:
        return render_template(
            "exception.html",
            exception_string="While getting User Info: " + str(e)
        )
    
    try:
        foods = search_food(request.form['food_description'])
    except Exception as e:
        return render_template(
            "exception.html",
            exception_string="While search for matching food during ate this: " + str(e)
        )
    
    try:
        return render_template(
            "atethis.html",
            user=me,
            search_pattern=request.form['food_description'],
            foods=foods
        )
    except Exception as e:
        return render_template(
            "exception.html",
            exception_string="While calling ate this: " + str(e)
        )


@app.route("/atethisthing/",methods=['POST'])
@flask_login.login_required
def atethisthing():
    try:
        #me = User(1) # Obviously need to update this later so that uid is posted or read from cookie
        me = flask_login.current_user
        fid = request.form['fid']
        quantity = request.form['quantity']
        insert_food_today( me.uid, fid, quantity, me.timezone )
    except Exception as e:
        return render_template(
            "exception.html",
            exception_string="While trying insert a record of what was eaten: " + str(e)
        )

    return redirect("/newtoday/", code=303)

@app.route("/atethisnewthing/",methods=['POST'])
@flask_login.login_required
def atethisnewthing():
    try:
        #me = User(1)
        me = flask_login.current_user
        quantity = request.form['quantity']
        precision = request.form['precision']
        description = request.form['description']
        calories = request.form['calories']
        insert_food_db( description, precision, calories )
        foods = search_food(request.form['description'])
        insert_food_today( me.uid, foods[0][0], quantity, me.timezone )
    except Exception as e:
        return render_template("exception.html",exception_string="While trying insert a record of a new thing that what was eaten: " + str(e))

    return redirect("/newtoday/", code=303)
    
@app.route("/report/",methods=['GET', 'POST'])
@flask_login.login_required
def report():
    try:
        #me = User(1)
        me = flask_login.current_user
    except Exception as e:
        return render_template(
            "exception.html",
            exception_string="While getting User Info: " + str(e)
        )

    return render_template(
        "under_construction.html",
        user=me,
        page_name="Report"
    )

@app.route("/user/",methods=['GET', 'POST'])
@flask_login.login_required
def user():
    try:
        #me = User(1)
        me = flask_login.current_user
    except Exception as e:
        return render_template(
            "exception.html",
            exception_string="While getting User Info: " + str(e)
        )

    return render_template(
        "under_construction.html",
        user=me,
        page_name="User Settings"
    )

# @app.route("/admin/",methods=['GET', 'POST'])
# @flask_login.login_required
# def admin():
#     try:
#         me = User(1)
#     except Exception as e:
#         return render_template(
#             "exception.html",
#             exception_string="While getting User Info: " + str(e)
#         )

#     return render_template(
#         "under_construction.html",
#         user=me,
#         page_name="Administrative Settings"
#     )

@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template("login.html")
    
    try:
        salty_hash = get_salty_hash(request.form['email'])
        sha256hash = hashlib.pbkdf2_hmac('sha256', str.encode(request.form['password']), str.encode(salty_hash[0][1]), 500000)
        if salty_hash[0][2] == sha256hash.hex():
            user = User(salty_hash[0][0])
            flask_login.login_user(user)
            return redirect("/newtoday/", code=303)
        
    except Exception as e:
        #return 'Bad Login'
        return render_template("exception.html",exception_string="Login trouble:: " + str(e))

@app.route('/protected/')
@flask_login.login_required
def protected():
    return 'Logged in as: ' + flask_login.current_user.username

@app.route('/logout/')
def logout():
    flask_login.logout_user()
    #return 'Logged out'
    return render_template("logout.html")

class User:
    def __init__(self, uid ):
        self.uid = uid
        try:
            user_lookup = self.lookup()
        except Exception as e:
            raise e
        self.username = user_lookup['name']
        self.birthdate = user_lookup['birthdate']
        self.height = user_lookup['height']
        self.mass = user_lookup['mass']
        self.iso_5218_sex = user_lookup['sex']
        self.systolic = user_lookup['systolic']
        self.diastolic = user_lookup['diastolic']
        self.timezone = user_lookup['timezone']
        self.activity_multiplier = 0 # Will update database later.
        self.authenticated = True
        self.active = True
        self.anonymous = False
    def lookup(self):
        try:
            conn = get_db_conn()
            sql = "SELECT users.name, users.birthdate, users.height, users.sex, health_metrics.date, health_metrics.mass, health_metrics.systolic, health_metrics.diastolic, users.timezone FROM users INNER JOIN health_metrics ON users.uid = health_metrics.uid WHERE users.uid = %s ORDER BY health_metrics.date DESC LIMIT 1;"
            curs = conn.cursor()
            curs.execute(sql, [self.uid])
            query_results = curs.fetchone()
            if query_results == None:
                raise Exception("No user info returned from database.")

            user_info = { "name": query_results[0], "birthdate": query_results[1], "height": query_results[2], "sex": query_results[3], "mass": query_results[5], "systolic": query_results[6], "diastolic": query_results[7], "timezone": query_results[8] }
            curs.close()
            conn.close()
            return user_info
        except Exception as e:
            raise e        
    def get_age(self):
        today = datetime.date.today()
        return  today.year - self.birthdate.year
    def display_sex(self):
        if self.iso_5218_sex == 1:
            return "Male"
        elif self.iso_5218_sex == 2:
            return "Female"
        else:
            raise Exception("Invalid value received for sex.")
    def harris_benedict( self ):
        # https://en.wikipedia.org/wiki/Harris%E2%80%93Benedict_equation1
        # 0: Sedentiary
        # 1: Light Exercise
        # 2: Moderate Exercise
        # 3: Heavy Exercise
        # 4: Very Heavy Exercise
        activity_multiplier = [ 1.2, 1.375, 1.55, 1.725, 1.9 ]
        if self.iso_5218_sex == 1:
            sex_modifer = 5
        elif self.iso_5218_sex == 2:
            sex_modifier = -161
        else:
            raise Exception( sex + " is not a valid iso_5218 value." )
        
        return int(((10 * self.mass) + ( 6.25 * self.height ) - ( 5 * self.get_age() ) +  sex_modifer) * activity_multiplier[self.activity_multiplier])
    def daily_caloric_target(self):
        return self.harris_benedict()
    def is_authenticated(self):
        return true
    def is_active(self):
        return true
    def is_anonymous(self):
        return false
    def get_id(self):
        return self.uid
        
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

def current_habits( uid, timezone ):
    try:
        sql = "SELECT exercise, stretch, sit, sss, journal, vitamins, brush_am, brush_pm, floss, water FROM habits WHERE uid = %s AND date = date(current_timestamp at time zone %s)"
        conn = get_db_conn()
        curs = conn.cursor()
        curs.execute(sql, [uid, timezone])
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

def update_habits( uid, exercise, stretch, sit, sss, journal, vitamins, brush_am, brush_pm, floss, water, timezone):
    try:
        sql = "INSERT INTO habits ( date, uid, exercise, stretch, sit, sss, journal, vitamins, brush_am, brush_pm, floss, water ) values ( date(current_timestamp at time zone %s), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s ) ON CONFLICT ( date, uid ) DO UPDATE set exercise = %s, stretch = %s, sit = %s, sss = %s, journal = %s, vitamins = %s, brush_am = %s, brush_pm = %s, floss = %s, water = %s"
        conn = get_db_conn()
        curs = conn.cursor()
        curs.execute(sql, [ timezone, uid, exercise, stretch, sit, sss, journal, vitamins, brush_am, brush_pm, floss, water, exercise, stretch, sit, sss, journal, vitamins, brush_am, brush_pm, floss, water ])
        conn.commit()
        curs.close()
        conn.close()
    except Exception as e:
        raise e

def eaten_today( uid, timezone ):
    try:
        sql = "SELECT food.description, eaten_daily.quantity, food.calories * eaten_daily.quantity, food.precision FROM eaten_daily INNER JOIN food ON eaten_daily.fid = food.fid WHERE eaten_daily.uid = %s AND date = date(current_timestamp at time zone %s)"
        conn = get_db_conn()
        curs = conn.cursor()
        curs.execute(sql,[uid, timezone])
        eaten_today = curs.fetchall()
        # Do I need a if eaten_today == None like in the current function?
        return eaten_today
    except Exception as e:
        raise e

def calories_today( uid, timezone ):
    try:
        total_daily_calories = 0
        sql = "SELECT eaten_daily.quantity, food.calories FROM eaten_daily INNER JOIN food on eaten_daily.fid = food.fid WHERE eaten_daily.uid = %s AND date = date(current_timestamp at time zone %s)"
        conn = get_db_conn()
        curs = conn.cursor()
        curs.execute(sql,[uid, timezone])
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

def insert_food_today( uid, fid, quantity, timezone ):
    try:
        sql = "INSERT INTO eaten_daily ( date, uid, fid, quantity ) values ( date(current_timestamp at time zone %s), %s, %s, %s );"
        conn = get_db_conn()
        curs = conn.cursor()
        curs.execute(sql, [timezone, uid, fid, quantity])
        conn.commit()
        curs.close()
        conn.close()
    except Exception as e:
        raise e

# Sophmoric Humor
def get_salty_hash( email ):
    try:
        sql = "SELECT uid, salt, hash from users where email = %s;"
        conn = get_db_conn()
        curs = conn.cursor()
        curs.execute(sql,[email])
        salty_hash = curs.fetchall()
        curs.close()
        conn.close()
        return salty_hash
    except Exception as e:
        raise e
