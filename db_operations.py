from db_connect import get_connection
from sqlalchemy.orm import sessionmaker, Session
from datetime import date
from sqlalchemy import create_engine, text
from sqlalchemy.exc import IntegrityError
from db_schema import (Base,
                       CXResource,
                       CXProject,
                       CXTask,
                       CXPortfolio,
                       CXProgramme,
                       CXTaskStatus,
                       ResourceType,
                       generate_sql)

# # Database connection setup
# DATABASE_URL = "postgresql://user:password@localhost:5432/mydatabase"
# engine = create_engine(DATABASE_URL)
# Session = sessionmaker(bind=engine)


class DBOperations:
    def __init__(self, db_config):
        """
        Initializes the database connection class using provided configuration.

        This class is responsible for setting up the connection to a PostgreSQL 
        database. It utilizes the `create_engine` function to establish the 
        connection string and creates the session to interact with the database. 
        The configuration for the connection is expected to include user, password, 
        host, and database name. The resulting engine and session are instance 
        attributes stored for further operations.

        :param db_config: Database configuration containing the keys "user", 
            "password", "host", and "dbname" necessary to establish the connection.
        :type db_config: dict
        """
        self._db_config = db_config
        self._engine = create_engine('postgresql+psycopg2://'
                           +db_config["user"]+':'
                           +db_config["password"]+'@'
                           +db_config["host"]+'/'
                           +db_config["dbname"])
        self._session = self._engine.connect()
            

    def add_resource(self, name, resource_type):
        """Return the given resource
        :param name: The name of the resource to be added.
        :param resource_type: The type/category of the resource to be added.
        :return: None
        """
        resource = CXResource(name=name, resource_type=resource_type)
        self._session.add(resource)
        try:
            self._session.commit()
            print(f"Added resource: {name}")
        except IntegrityError:
            self._session.rollback()
            print("Error: Could not add resource.")
        return 

    def add_project(self, title, owner_id, start_date):
        """
        :param title: The title of the project to be added.
        :param owner_id: The ID of the owner responsible for the project.
        :param start_date: The starting date of the project.
        :return: None, the function commits the project to the session or rolls back in case of an error.
        """
        project = CXProject(title=title, owner_id=owner_id, start_date=start_date)
        self._session.add(project)
        try:
            self._session.commit()
            print(f"Added project: {title}")
        except IntegrityError:
            self._session.rollback()
            print("Error: Could not add project.")

    def add_task(self, title, status, project_id):
        """
        :param title: The title of the task to be added.
        :param status: The status of the task (e.g., pending, completed).
        :param project_id: The identifier of the project to which the task belongs.
        :return: None
        """
        task = CXTask(title=title, status=status, project_id=project_id)
        self._session.add(task)
        try:
            self._session.commit()
            print(f"Added task: {title}")
        except IntegrityError:
            self._session.rollback()
            print("Error: Could not add task.")

    def list_projects(self):
        """Retrieves and prints a list of all projects from the database.

        :return: A list of CXProject objects representing all projects.
        """
        projects = self._session.query(CXProject).all()
        for project in projects:
            print(f"Project ID: {project.id}, Title: {project.title}, Owner ID: {project.owner_id}, Start Date: {project.start_date}")
        return projects

    def list_tasks_by_project(self, project_id):
        """
        :param project_id: The ID of the project for which the tasks need to be retrieved.
        :return: A list of CXTask objects associated with the given project ID.
        """
        tasks = self._session.query(CXTask).filter(CXTask.project_id == project_id).all()
        for task in tasks:
            print(f"Task ID: {task.id}, Title: {task.title}, Status: {task.status}")
        return tasks

    def add_portfolio(self, title, goal, owner_id, start_date):
        """
        :param title: The title of the portfolio being created.
        :param goal: The goal or objective of the portfolio.
        :param owner_id: The ID of the owner or creator of the portfolio.
        :param start_date: The starting date of the portfolio.
        :return: None
        """
        portfolio = CXPortfolio(title=title, goal=goal, owner_id=owner_id, start_date=start_date)
        self._session.add(portfolio)
        try:
            self._session.commit()
            print(f"Added portfolio: {title}")
        except IntegrityError:
            self._session.rollback()
            print("Error: Could not add portfolio.")

    def add_programme(self, title, owner_id, start_date):
        """
        :param title: The title of the programme to be added.
        :param owner_id: The identifier of the owner associated with the programme.
        :param start_date: The date on which the programme starts.
        :return: None
        """
        programme = CXProgramme(title=title, owner_id=owner_id, start_date=start_date)
        self._session.add(programme)
        try:
            self._session.commit()
            print(f"Added programme: {title}")
        except IntegrityError:
            self._session.rollback()
            print("Error: Could not add programme.")
            
    

    def clear_database(self):
        """Clears all data from the database."""
        try:
            self._session.query(CXTask).delete()
            self._session.query(CXProject).delete()
            self._session.query(CXPortfolio).delete()
            self._session.query(CXProgramme).delete()
            self._session.commit()
            self._session.query(CXResource).delete()
            self._session.commit()
            print("Cleared all data from the database.")
        except Exception as e:
            self._session.rollback()
            print(f"Error: Could not clear database. {str(e)}")

    # Create a backup of the database by exporting all data
    def backup_database(self, backup_session):
        """
        Backups all data from the current database session to a backup session.
        
        :param backup_session: The database session where the backup will be stored.
        """
        try:
            # Backup CXResource
            resources = self._session.query(CXResource).all()
            for resource in resources:
                backup_session.add(CXResource(name=resource.name, resource_type=resource.resource_type))

            # Backup CXProject
            projects = self._session.query(CXProject).all()
            for project in projects:
                backup_session.add(CXProject(
                    title=project.title,
                    owner_id=project.owner_id,
                    start_date=project.start_date
                ))

            # Backup CXTask
            tasks = self._session.query(CXTask).all()
            for task in tasks:
                backup_session.add(CXTask(
                    title=task.title,
                    status=task.status,
                    project_id=task.project_id
                ))

            # Backup CXPortfolio
            portfolios = self._session.query(CXPortfolio).all()
            for portfolio in portfolios:
                backup_session.add(CXPortfolio(
                    title=portfolio.title,
                    goal=portfolio.goal,
                    owner_id=portfolio.owner_id,
                    start_date=portfolio.start_date
                ))

            # Backup CXProgramme
            programmes = self._session.query(CXProgramme).all()
            for programme in programmes:
                backup_session.add(CXProgramme(
                    title=programme.title,
                    owner_id=programme.owner_id,
                    start_date=programme.start_date
                ))

            # Commit backup
            backup_session.commit()
            print("Database backup created successfully.")
        except Exception as e:
            backup_session.rollback()
            print(f"Error: Could not create database backup. {str(e)}")

    def database_health_check(self, interaction_date=None):
        """
        Provides a general health check of the database, including its contents
        and the number of interactions (records) on a given date.
        
        :param interaction_date: (Optional) Specific date to filter interactions, expected to be a datetime.date object.
        :return: None. Prints the database health overview.
        """
        try:
            # General counts for each table
            resources_count = self._session.query(CXResource).count()
            projects_count = self._session.query(CXProject).count()
            tasks_count = self._session.query(CXTask).count()
            portfolios_count = self._session.query(CXPortfolio).count()
            programmes_count = self._session.query(CXProgramme).count()

            print("Database Health Check:")
            print(f"Total Resources: {resources_count}")
            print(f"Total Projects: {projects_count}")
            print(f"Total Tasks: {tasks_count}")
            print(f"Total Portfolios: {portfolios_count}")
            print(f"Total Programmes: {programmes_count}")

            # Filter interactions for a specific date if provided
            if interaction_date:
                interactions_count = self._session.query(CXTask).filter(
                    CXTask.date == interaction_date
                ).count()
                print(f"Interactions on {interaction_date}: {interactions_count}")
            else:
                print("No interaction date provided. Skipping interaction count.")
        except Exception as e:
            print(f"Error during health check: {str(e)}")

    def setup_user_access(self, user):
        """
        Grants defined rights access to the provided user by executing SQL statements.
        
        :param user: The username for whom the rights should be configured.
        :return: None.
        """
        sql_query = f"""
        GRANT USAGE ON SCHEMA seaview TO {user};
        GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA seaview TO {user};
        ALTER DEFAULT PRIVILEGES IN SCHEMA seaview GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {user};
        """
        try:
            self._session.execute(text(sql_query))
            self._session.commit()
            print(f"Access rights successfully granted to user: {user}")
        except Exception as e:
            self._session.rollback()
            print(f"Error setting up user access for {user}: {str(e)}")

    def cascade_delete_schema(self, schema_name):
        """
        Deletes all objects inside a schema and drops the schema itself in a cascading manner.
    
        :param schema_name: The name of the schema to be deleted.
        :return: None
        """
        sql_query = f"DROP SCHEMA IF EXISTS {schema_name} CASCADE;"
        try:
            self._session.execute(text(sql_query))
            self._session.commit()
            print(f"Schema '{schema_name}' deleted successfully.")
        except Exception as e:
            self._session.rollback()
            print(f"Error deleting schema '{schema_name}': {str(e)}")

    def regenerate_schema(self, schema_name):
        """
        Regenerates the database schema by first performing a cascading delete
        of the existing schema and then regenerating it using SQL commands
        derived from the current database configuration.

        :param schema_name: The name of the schema to be regenerated.
        :type schema_name: str
        :return: None
        """
        self.cascade_delete_schema(schema_name)
        generate_sql(self._db_config)

