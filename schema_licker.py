import psycopg2
from psycopg2 import sql
from pydantic import BaseModel

#
# This can be utilized on request for apps root directory.
# to get an updated schema for a specific table.
# Most likely, this app will only need to interact with one table.
# Constants (e.g. Cost-Codes) will be added as a setup step for the database.
#

# Define a function to connect to the PostgreSQL database
def connect_to_postgres(host, database, user, password):
    try:
        connection = psycopg2.connect(
            host=host,
            database=database,
            user=user,
            password=password
        )
        return connection
    except psycopg2.Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
        return None


# Define a function to fetch the table's columns and data types
def fetch_table_columns(connection, table_name):
    cursor = connection.cursor()
    query = sql.SQL("SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s;")
    cursor.execute(query, (table_name,))
    columns = cursor.fetchall()
    cursor.close()
    return columns


# Define a function to create a Pydantic BaseModel
def create_pydantic_model(table_name, columns):
    class TableModel(BaseModel):
        class Config:
            orm_mode = True
    
    # Create fields for the Pydantic model dynamically
    for column_name, data_type in columns:
        data_type = data_type.upper()  # Convert data type to uppercase for Pydantic
        setattr(TableModel, column_name, (data_type,))
    
    # Rename the Pydantic model with the table name
    TableModel.__name__ = table_name
    return TableModel


# Proxy function to simplify development
def create_model_from_table(connection, table_name):
    columns = fetch_table_columns(connection, table_name)
    return create_pydantic_model(table_name, columns)
