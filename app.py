from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def dashboard():
    username="Nathan"
    return render_template("dashboard.html",username=username)
