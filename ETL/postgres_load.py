import psycopg2
import pandas as pd

# Database connection details
DB_HOST = "localhost"
DB_NAME = "Project 3"
DB_USER = "postgres"
DB_PASSWORD = "Ricola#1"
DB_PORT = 5432  # Default PostgreSQL port

def create_tables(cursor):
    """Create tables in the PostgreSQL database."""
    create_demographic_table = """
    CREATE TABLE IF NOT EXISTS demographic_data (
        serialno VARCHAR PRIMARY KEY,
        rac1p INTEGER,
        paoc INTEGER,
        pernp INTEGER,
        mar INTEGER,
        agep INTEGER,
        schl INTEGER,
        sex INTEGER
    );
    """
    
    create_origins_table = """
    CREATE TABLE IF NOT EXISTS origins (
        serialno VARCHAR PRIMARY KEY,
        rac1p INTEGER,
        lanp INTEGER,
        anc1p INTEGER
    );
    """
    
    cursor.execute(create_demographic_table)
    cursor.execute(create_origins_table)
    print("Tables created successfully.")

def import_csv_to_table(cursor, table_name, csv_file):
    """Import CSV data into the specified PostgreSQL table."""
    df = pd.read_csv(csv_file)
    
    # Generate column placeholders for SQL insertion
    columns = ", ".join(df.columns)
    placeholders = ", ".join(["%s"] * len(df.columns))
    insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) ON CONFLICT (serialno) DO NOTHING;"
    
    # Convert DataFrame rows to tuples
    data = [tuple(row) for row in df.to_numpy()]
    
    # Execute batch insertion
    cursor.executemany(insert_query, data)
    print(f"Data imported into table '{table_name}' from '{csv_file}'.")

def main():
    try:
        # Connect to PostgreSQL database
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("Connected to the database.")

        # Step 1: Create tables
        create_tables(cursor)
        
        # Step 2: Import CSV files into tables
        import_csv_to_table(cursor, "demographic_data", "demographic_data.csv")
        import_csv_to_table(cursor, "origins", "origins.csv")
        
        print("CSV data imported successfully.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        if conn:
            cursor.close()
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    main()
