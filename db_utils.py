from db_connect import get_connection
from config import DB_CONFIG, DB_ADMIN_CONFIG  # Assuming the config file contains a dictionary named DATABASE_CONFIG

def execute_raw_query(connection_config, query):
    """
    :param connection_config: Configuration details required to establish a database connection.
    :type connection_config: dict
    :param query: The raw SQL query string to be executed against the database.
    :type query: str
    :return: The result of the query if it's a SELECT statement; otherwise, None for non-SELECT statements.
    :rtype: list or None
    """
    connection = get_connection(connection_config)
    try:
        cursor = connection.cursor()
        cursor.execute(query)
        if query.strip().upper().startswith("SELECT"):
            result = cursor.fetchall()
        else:
            result = None
            connection.commit()
        cursor.close()
        return result
    except Exception as e:
        print(f"Error executing query: {e}")
        return None
    finally:
        if connection:
            connection.close()


def test_connection():
    """
    Tests database connections for multiple configurations.

    Iterates over each configuration in the test setup list, tries to establish
    a connection, and prints the status of the connection attempt.
    If an error occurs during the connection attempt, it prints the error details.

    :return: None
    """
    test_setups = [DB_CONFIG, DB_ADMIN_CONFIG]
    for tst in test_setups:
        try:
            connection = get_connection(tst)
            if connection:
                print("Connection successfully established.")
                connection.close()
            else:
                print("Failed to establish connection.")
        except Exception as e:
            print(f"Error testing connection: {e}")


