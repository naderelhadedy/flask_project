from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class Citizen(db.Model):
    citizen_first_name = db.Column(db.String(12), nullable=False)
    citizen_father_name = db.Column(db.String(30), nullable=False)
    citizen_mother_name = db.Column(db.String(30), nullable=False)
    citizen_dob = db.Column(db.DateTime, default=datetime.utcnow)
    citizen_gender = db.Column(db.String(8), nullable=False)
    citizen_id = db.Column(db.Integer, primary_key=True)

    def __repr__(self):
        return f"{self.citizen_first_name} {self.citizen_father_name} " \
               f"{{ID: {self.citizen_id}, Gender: {self.citizen_gender}," \
               f" Mother's Name: {self.citizen_mother_name}," \
               f" DOB: {self.citizen_dob}}}"

    def __str__(self):
        return f"{self.citizen_first_name} <{self.citizen_id}>"


@app.route("/")
def index():
    total_citizens_count = len(Citizen.query.all())
    current_year = datetime.utcnow().year
    return render_template("index.html", total_count=total_citizens_count, current_year=current_year)


@app.route("/add_citizen", methods=['POST', 'GET'])
def add_citizen():
    if request.method == 'POST':
        citizen_name = request.form['citizen_name']
        citizen_father_name = request.form['citizen_father_name']
        citizen_mother_name = request.form['citizen_mother_name']
        try:
            options = request.form['options']
        except:
            return render_template('not_complete_alert.html')

        if not all(request.form.values()):
            return render_template('not_complete_alert.html')

        current = datetime.utcnow()
        citizen_id = int(f"{1 if options == 'Male' else 2}{str(current.year)[-2:]}"
                         f"{current.month:02d}{current.day:02d}"
                         f"{current.hour:02d}{current.minute:02d}"
                         f"{current.second:02d}{str(current.microsecond)[-1]}")

        new_citizen = Citizen(citizen_first_name=citizen_name, citizen_father_name=citizen_father_name,\
                              citizen_mother_name=citizen_mother_name, citizen_gender=options,\
                              citizen_id=citizen_id)

        try:
            db.session.add(new_citizen)
            db.session.commit()
            return render_template("citizen_added.html", citizen_id=citizen_id,
                                   citizen_fullname=citizen_name+' '+citizen_father_name)
        except:
            return "There was an issue while adding this citizen"
    else:
        return render_template("add_citizen.html")


@app.route("/get_info", methods=['POST', 'GET'])
def get_info():
    if request.method == 'POST':
        citizen_id = request.form['password']
        if len(str(citizen_id)) != 14:
            return render_template("digits_alert.html")
        target_citizen = Citizen.query.filter_by(citizen_id=citizen_id).first()
        if not target_citizen:
            return render_template("not_found_alert.html")
        return render_template("target_citizen.html", target_citizen=repr(target_citizen))
    else:
        return render_template("get_info.html")


@app.route("/view_all_citizens")
def view_all_citizens():
    citizens = Citizen.query.order_by(Citizen.citizen_dob).all()
    return render_template("view_all_citizens.html", citizens=citizens)


@app.route("/delete/<int:cit_id>")
def delete_citizen(cit_id):
    citizen_to_delete = Citizen.query.get_or_404(cit_id)

    try:
        db.session.delete(citizen_to_delete)
        db.session.commit()
        return redirect(url_for('view_all_citizens'))
    except:
        return render_template("delete_alert.html")
