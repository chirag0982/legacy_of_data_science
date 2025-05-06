from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text  # Add this import at the top

import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///heart.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class HeartData(db.Model):
    __tablename__ = 'heart_data'
    id = db.Column(db.Integer, primary_key=True)
    Age = db.Column(db.Float)
    Sex = db.Column(db.Float)
    ChestPainType = db.Column(db.Float)
    RestingBP = db.Column(db.Float)
    Cholesterol = db.Column(db.Float)
    FastingBS = db.Column(db.Float)
    RestingECG = db.Column(db.Float)
    MaxHR = db.Column(db.Float)
    ExerciseAngina = db.Column(db.Float)
    Oldpeak = db.Column(db.Float)
    ST_Slope = db.Column(db.Float)
    HeartDisease = db.Column(db.Float)

class TransformedHeartData(db.Model):
    __tablename__ = 'transformed_heart_data'
    id = db.Column(db.Integer, primary_key=True)
    Age = db.Column(db.Float)
    MaxHR_Age_Ratio = db.Column(db.Float)
    NormalizedCholesterol = db.Column(db.Float)

def load_data_from_csv(csv_file):
    with app.app_context():
        data = pd.read_csv(csv_file)
        data.reset_index(inplace=True)  # Reset index to create an automatic 'index' column
        data.rename(columns={'index': 'id'}, inplace=True)  # Rename 'index' column to 'id'
        data.to_sql('heart_data', db.engine, index=False, if_exists='replace')  # 'index=False' avoids creating an extra unnamed column

def transform_data():
    from sqlalchemy import text
    with db.engine.connect() as connection:
        df = pd.read_sql(text('SELECT * FROM heart_data'), connection)

        df['MaxHR_Age_Ratio'] = df['MaxHR'] / df['Age']
        df['NormalizedCholesterol'] = (df['Cholesterol'] - df['Cholesterol'].mean()) / df['Cholesterol'].std()

        transformed_df = df[['id', 'Age', 'MaxHR_Age_Ratio', 'NormalizedCholesterol']]

        transformed_df.to_sql('transformed_heart_data', connection, index=False, if_exists='replace')


@app.route('/')
def index():
    return 'Flask App with SQLAlchemy'

@app.route('/data')
def view_data():
    heart_data = HeartData.query.all()
    data = [{column.name: getattr(entry, column.name) for column in entry.__table__.columns} for entry in heart_data]
    return jsonify(data)

@app.route('/ETL')
def view_transformed_data():
    transformed_data = TransformedHeartData.query.all()
    data = [{column.name: getattr(entry, column.name) for column in entry.__table__.columns} for entry in transformed_data]
    return jsonify(data)

if __name__ == '__main__':
    with app.app_context():
        db.drop_all()  # Drop all tables for demonstration purposes
        db.create_all()  # Create all tables based on models
        load_data_from_csv('heart.csv')
        transform_data()  # Perform ETL
    app.run(debug=True)
