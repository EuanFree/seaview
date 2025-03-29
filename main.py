from db_utils import test_connection
from db_schema import generate_sql
from config import DB_ADMIN_CONFIG

from db_operations import DBOperations, DBExampleProjectSetup

if __name__ == "__main__":
    test_connection()
    db_operator = DBOperations(DB_ADMIN_CONFIG)
    #db_operator.clear_database()
    db_operator.regenerate_schema('seaview')
    #generate_sql(DB_ADMIN_CONFIG)
    db_operator.setup_user_access('nt_client')
    db_example_generator = DBExampleProjectSetup(nPortfolios = 3,
                                                 nProgrammes = 2,
                                                 nProjects = 10,
                                                 nTasks = 500,
                                                 nResources = 30)
    db_example_generator.generate_example_data(db_operator)
