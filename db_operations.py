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
                       ResourceDepartment,
                       CXProjectDependencyAssociation,
                       CXTaskDependencies,
                       CXProgrammeDependencyAssociation,
                       CXTaskChange,
                       CXProjectGanttPermissions,
                       CXProjectTaskUserSetup,
                       CXProjectUserSetup,
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
        self._Session = sessionmaker(bind=self._engine)  # Initialize Session factory
        self._session = self._Session()  # Create session instance

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
        except IntegrityError as e:
            self._session.rollback()
            print(f"Error: Could not add resource. Reason: {str(e)}")
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
        except IntegrityError as e:
            self._session.rollback()
            print(f"Error: Could not add project. Reason: {str(e)}")

    def add_task(self, title, status, project_id, start_date=None, end_date=None):
        """
        Adds a new task to the database session and commits the changes. If any error occurs during
        the commit, such as an IntegrityError, the transaction is rolled back to maintain the state
        of the session.

        :param title: Title of the task.
        :type title: str
        :param status: Current status of the task.
        :type status: str
        :param project_id: Identifier of the project to which the task belongs.
        :type project_id: int
        :param start_date: The start date of the task. Optional.
        :type start_date: datetime or None
        :param end_date: The end date of the task. Optional.
        :type end_date: datetime or None
        :return: None
        """
        task = CXTask(title=title, status=status, project_id=project_id, start_date=start_date, end_date=end_date)
        self._session.add(task)
        try:
            self._session.commit()
            print(f"Added task: {title}")
        except IntegrityError as e:
            self._session.rollback()
            print(f"Error: Could not add task. Reason: {str(e)}")

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
        except IntegrityError as e:
            self._session.rollback()
            print(f"Error: Could not add portfolio. Reason: {str(e)}")

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
        except IntegrityError as e:
            self._session.rollback()
            print(f"Error: Could not add programme. Reason: {str(e)}")

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


class DBExampleProjectSetup:

    def __init__(self, nPortfolios=1, nProgrammes=1, nProjects=4, nTasks=40, nResources=10):
        """

        """
        self.nPortfolios = nPortfolios
        self.nProgrammes = nProgrammes
        self.nProjects = nProjects
        self.nTasks = nTasks
        self.nResources = nResources

    def generate_example_data(self, db_operator):
        """
        Generates example data with the specified number of entities and interconnections, including random dependencies.
    
        This method creates portfolios, programmes, projects, tasks, and resources,
        interlinking them in a random fashion. Tasks are provided with random 
        start and finish dates, and some tasks have dependencies on others.
    
        :param db_operator: An instance of DBOperations to interact with the database.
        """
        import random
        from datetime import timedelta

        resource_list = ['PERSON','FACILITY','PRODUCT','GENERIC']
        task_status_list = ['BLOCKED','BACKLOG','IN_PROGRESS','COMPLETE','CANCELLED']
        # Create resources
        resource_ids = []
        for i in range(self.nResources):
            resource_name = f"Resource {i + 1}"
            #resource_type = f"Type {i % 5}"  # Assign some example resource types
            resource_type = random.choice(resource_list)

            db_operator.add_resource(name=resource_name, resource_type=resource_type)
            resource_ids.append(resource_name)  # Collecting resource names (or IDs if applicable)

        # Create portfolios
        portfolio_ids = []
        for i in range(self.nPortfolios):
            title = f"Portfolio {i + 1}"
            goal = f"Goal {i + 1}"
            start_date = date.today()
            db_operator.add_portfolio(title=title, goal=goal, owner_id=1, start_date=start_date)
            portfolio_ids.append(i + 1)  # Collecting dummy IDs for portfolio (assuming sequential IDs)

        # Create programmes
        programme_ids = []
        for i in range(self.nProgrammes):
            title = f"Programme {i + 1}"
            start_date = date.today()
            db_operator.add_programme(title=title, owner_id=1, start_date=start_date)
            programme_ids.append(i + 1)  # Collecting dummy IDs for programmes (assuming sequential IDs)

        # Randomly assign programmes to portfolios
        for programme_id in programme_ids:
            random_portfolio_id = random.choice(portfolio_ids)
            # Assuming a method to link programmes to portfolios exists
            print(f"Linking programme {programme_id} to portfolio {random_portfolio_id}")

        # Create projects
        project_ids = []
        for i in range(self.nProjects):
            title = f"Project {i + 1}"
            start_date = date.today()
            db_operator.add_project(title=title, owner_id=1, start_date=start_date)
            project_ids.append(i + 1)  # Collecting dummy IDs for projects (assuming sequential IDs)

        # Randomly assign projects to programmes
        for project_id in project_ids:
            random_programme_id = random.choice(programme_ids)
            # Assuming a method to link projects to programmes exists
            print(f"Linking project {project_id} to programme {random_programme_id}")

        # Create tasks with random start and finish dates
        task_ids = []
        for i in range(self.nTasks):
            task_title = f"Task {i + 1}"
            status = random.choice(task_status_list)
            project_id = random.choice(project_ids)  # Assign tasks randomly to projects
            start_date = date.today() + timedelta(days=random.randint(0, 30))
            finish_date = start_date + timedelta(days=random.randint(1, 10))  # Ensure finish is after start
            db_operator.add_task(title=task_title, status=status, project_id=project_id)
            task_ids.append(i + 1)  # Collecting dummy IDs for tasks (assuming sequential IDs)
            print(f"Created task: {task_title}, start_date: {start_date}, finish_date: {finish_date}")

        # Create random task dependencies
        for task_id in task_ids:
            if random.random() > 0.5:  # 50% chance to create a dependency
                dependent_task_id = random.choice(task_ids)
                if dependent_task_id != task_id:  # Avoid self-dependency
                    # Assuming a method to add task dependencies exists
                    print(f"Task {task_id} depends on Task {dependent_task_id}")

        # Assign existing resources to tasks
        for resource_name in resource_ids:
            assigned_task_id = random.choice(task_ids)
            print(f"Assigning resource {resource_name} to task {assigned_task_id}")

        print("Example data generation complete.")
