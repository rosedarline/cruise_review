from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from send_mail import send_mail

app = Flask(__name__)

ENV = 'dev'
if ENV == 'dev':
    app.debug = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:@localhost/dealership'
else:
    app.debug = False
    app.config['SQLALCHEMY_DATABASE_URI'] = ''

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    customer = db.Column(db.String(200), unique=True)
    ships = db.Column(db.String(200))
    rating = db.Column(db.Integer)
    comments = db.Column(db.Text())

    def __init__(self, customer, ships, rating, comments):
        self.customer = customer
        self.ships = ships
        self.rating = rating
        self.comments = comments


@app.route('/')
def index():
    reviews = db.session.query(feedback).all()
    return render_template('index.html', reviews=reviews)


@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        customer = request.form['customer']
        ships = request.form['ships']
        rating = request.form['rating']
        comments = request.form['comments']
        reviews = db.session.query(feedback).all()
        print(customer, ships, rating, comments, reviews)
        if customer == '' or ships == '':
            return render_template('index.html', message='Please enter required fields', reviews=reviews)
        if db.session.query(feedback).filter(feedback.customer == customer).count() == 0:
            data = feedback(customer, ships, rating, comments)
            db.session.add(data)
            db.session.commit()
            send_mail(customer, ships, rating, comments)
            return render_template('success.html')
        return render_template('index.html', message='You have already submitted feedback', reviews=reviews)


if __name__ == '__main__':
    app.run()
