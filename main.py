from db_utils import test_connection
from db_schema import generate_sql
from config import DB_ADMIN_CONFIG

from db_operations import DBOperations

if __name__ == "__main__":
    test_connection()
    db_operator = DBOperations(DB_ADMIN_CONFIG)
    #db_operator.clear_database()
    db_operator.regenerate_schema('seaview')
    #generate_sql(DB_ADMIN_CONFIG)
    db_operator.setup_user_access('nt_client')

