import psycopg2
from config import DB_CONFIG  # Assuming you have a 'config.py' with credentials


def get_connection(config):
    """
    Establishes a connection to a PostgreSQL database using the configuration provided in the config dictionary.

    :param config: A dictionary containing the database connection parameters.
    :return: A psycopg2 connection object if the connection is successful, or None if an error occurs.
    """
    try:
        connection = psycopg2.connect(
            dbname=config["dbname"],
            user=config["user"],
            password=config["password"],
            host=config["host"],
            port=config["port"]
        )
        return connection
    except psycopg2.Error as e:
        print(f"Error while connecting to the database: {e}")
        return None

