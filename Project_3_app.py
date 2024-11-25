import psycopg2
import pandas as pd
from flask import Flask, request, jsonify

# Database connection details
DB_HOST = "localhost"
DB_NAME = "Project 3"
DB_USER = "postgres"
DB_PASSWORD = "Ricola#1"
DB_PORT = 5432

# Flask app initialization
app = Flask(__name__)

def get_db_connection():
    """Establish a connection to the PostgreSQL database."""
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=DB_PORT
    )

@app.route('/data/filter', methods=['GET'])
def filter_data():
    """Endpoint to filter data from the demographic_data table."""
    min_age = request.args.get('min_age', type=int, default=0)
    max_age = request.args.get('max_age', type=int, default=120)
    race = request.args.get('race', type=int, default=None)
    education = request.args.get('education', type=int, default=None)
    income = request.args.get('income', type=int, default=None)
    sex = request.args.get('sex', type=int, default=None)

    query = "SELECT * FROM demographic_data WHERE agep BETWEEN %s AND %s"
    params = [min_age, max_age]

    if race is not None:
        query += " AND rac1p = %s"
        params.append(race)

    if education is not None:
        query += " AND schl = %s"
        params.append(education)

    if income is not None:
        query += " AND pernp >= %s"
        params.append(income)

    if sex is not None:
        query += " AND sex = %s"
        params.append(sex)

    print("Generated Query:", query)
    print("Parameters:", params)

    try:
        conn = get_db_connection()
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

@app.route('/data/origins', methods=['GET'])
def get_origins_data():
    """Endpoint to fetch data from the origins table by serial number."""
    serialno = request.args.get('serialno', type=str)
    if not serialno:
        return jsonify({"error": "Missing serialno parameter"}), 400

    query = "SELECT * FROM origins WHERE serialno = %s"

    try:
        conn = get_db_connection()
        df = pd.read_sql_query(query, conn, params=[serialno])
        conn.close()

        if df.empty:
            return jsonify({"message": "No data found for the provided serial number"}), 404

        return jsonify(df.to_dict(orient='records'))
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
