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
                       generate_sql, CXTaskResourceAssociation)

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


    def add_resource(self, name, resource_type, username=None):
        """Return the given resource
        :param name: The name of the resource to be added.
        :param resource_type: The type/category of the resource to be added.
        :return: None
        """
        resource = CXResource(name=name, resource_type=resource_type, username=username)
        self._session.add(resource)
        try:
            self._session.commit()
            print(f"Added resource: {name}")
        except IntegrityError as e:
            self._session.rollback()
            print(f"Error: Could not add resource. Reason: {str(e)}")
        return

    def add_project(self, title, owner_id, start_date, portfolio_id=None, programme_id=None):
        """
        :param title: The title of the project to be added.
        :param owner_id: The ID of the owner responsible for the project.
        :param start_date: The starting date of the project.
        :return: None, the function commits the project to the session or rolls back in case of an error.
        """
        project = CXProject(title=title,
                            owner_id=owner_id,
                            start_date=start_date,
                            portfolio_id=portfolio_id,
                            programme_id=programme_id)
        self._session.add(project)
        try:
            self._session.commit()
            print(f"Added project: {title}")
        except IntegrityError as e:
            self._session.rollback()
            print(f"Error: Could not add project. Reason: {str(e)}")

    def add_task(self, title, status, project_id, start_date=None, end_date=None, duration=None, owner_id=None):
        """
        Adds a new task to the database with the given attributes.
    
        Detailed Summary:
        This function creates a new instance of the `CXTask` class using the provided
        parameters and adds it to the current database session. The session is then
        committed to save the task into the database. If an `IntegrityError` occurs during
        the commit process, the session is rolled back and an error message is displayed.
    
        :param title: The title of the task.
        :type title: str
        :param status: The current status of the task.
        :type status: str
        :param project_id: The identifier of the project to which the task belongs.
        :type project_id: int
        :param start_date: The date when the task starts. Optional.
        :type start_date: date, optional
        :param end_date: The date when the task ends. Optional.
        :type end_date: date, optional
        :param duration: The duration of the task. Optional.
        :type duration: int, optional
        :return: None
        """
        task = CXTask(title=title, status=status, project_id=project_id, start_date=start_date, end_date=end_date,
                      duration=duration)
        self._session.add(task)
        try:
            self._session.commit()
            print(f"Added task: {title}")
        except IntegrityError as e:
            self._session.rollback()
            print(f"Error: Could not add task. Reason: {str(e)}")

    def add_task_resource_link(self, task_id, resource_id):
        link = CXTaskResourceAssociation(task_id=task_id, resource_id=resource_id)
        self._session.add(link)
        try:
            self._session.commit()
            print(f"Added task resource link for task ID: {task_id}")
            print(f"Added resource ID: {resource_id} to task ID: {task_id}")
        except IntegrityError as e:
            self._session.rollback()
            print(f"Error: Could not add task resource link. Reason: {str(e)}")

    def add_project_gantt_permissions(self, user_id, project_id):
        pgp = CXProjectGanttPermissions(user_id=user_id, project_id=project_id)
        self._session.add(pgp)
        try:
            self._session.commit()
            print(f"Added project Gantt permissions for project ID: {project_id}")
        except IntegrityError as e:
            self._session.rollback()
            print(f"Error: Could not add project Gantt permissions. Reason: {str(e)}")

    def add_project_task_user_setup(self, task_id, user_id, project_id):
        ptus = CXProjectTaskUserSetup(task_id=task_id, user_id=user_id, project_id=project_id)
        self._session.add(ptus)
        try:
            self._session.commit()
            print(f"Added project task user setup for project ID: {project_id}")
        except IntegrityError as e:
            self._session.rollback()
            print(f"Error: Could not add project task user setup. Reason: {str(e)}")


    def add_task_dependency(self, predecessor_id, successor_id):
        """
        Creates a dependency relationship between two tasks in the database.
    
        :param predecessor_id: The ID of the predecessor task in the dependency relationship.
        :type predecessor_id: int
        :param successor_id: The ID of the successor task in the dependency relationship.
        :type successor_id: int
        """
        dependency = CXTaskDependencies(predecessor_id=predecessor_id, successor_id=successor_id)
        self._session.add(dependency)
        try:
            self._session.commit()
            print(f"Task {successor_id} now depends on Task {predecessor_id}")
        except IntegrityError as e:
            self._session.rollback()
            print(f"Error: Could not add task dependency. Reason: {str(e)}")

    def get_task_project_id(self, task_id):
        """
        Retrieves the project ID associated with a given task ID.
    
        :param task_id: The ID of the task whose project information is to be retrieved.
        :type task_id: int
        :return: The project ID associated with the specified task or None if not found.
        :rtype: int or None
        """
        try:
            task = self._session.query(CXTask).filter(CXTask.id == task_id).first()
            if task:
                return task.project_id
            print(f"No task found with ID: {task_id}")
            return None
        except Exception as e:
            print(f"Error retrieving project ID for task {task_id}: {str(e)}")
            return None

    def get_task_start_date(self, task_id):
        """
        Retrieves the start date of a task with the given task ID.
    
        :param task_id: The ID of the task whose start date needs to be retrieved.
        :type task_id: int
        :return: The start date of the task or None if not found.
        :rtype: datetime.date or None
        """
        try:
            task = self._session.query(CXTask).filter(CXTask.id == task_id).first()
            if task:
                return task.start_date
            print(f"No task found for ID: {task_id}")
            return None
        except Exception as e:
            print(f"Error retrieving start date for task {task_id}: {str(e)}")

    def get_task_end_date(self, task_id):
        """
        Retrieves the end date of a task with the given task ID.
    
        :param task_id: The ID of the task whose start date needs to be retrieved.
        :type task_id: int
        :return: The end date of the task or None if not found.
        :rtype: datetime.date or None
        """
        try:
            task = self._session.query(CXTask).filter(CXTask.id == task_id).first()
            if task:
                return task.end_date
            print(f"No task found for ID: {task_id}")
            return None
        except Exception as e:
            print(f"Error retrieving end date for task {task_id}: {str(e)}")

    def get_task_duration(self, task_id):
        """
        Retrieves the duration of a task with the given task ID.
    
        :param task_id: The ID of the task whose duration needs to be retrieved.
        :type task_id: int
        :return: The duration of the task or None if not found.
        :rtype: int or None
        """
        try:
            task = self._session.query(CXTask).filter(CXTask.id == task_id).first()
            if task:
                return task.duration
            print(f"No task found with ID: {task_id}")
            return None
        except Exception as e:
            print(f"Error retrieving duration for task {task_id}: {str(e)}")

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

    def add_programme(self, title, owner_id, start_date, portfolio_id=None):
        """
        :param title: The title of the programme to be added.
        :param owner_id: The identifier of the owner associated with the programme.
        :param start_date: The date on which the programme starts.
        :return: None
        """
        programme = CXProgramme(title=title,
                                owner_id=owner_id,
                                start_date=start_date,
                                portfolio_id=portfolio_id)
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
        GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA seaview TO {user};
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

    # This is purely for the example generation - not expected to be used in any other context
    def update_task_project(self, task_id, project_id):
        """
        Updates the project ID of a task with the given task ID.
        
        :param task_id: The ID of the task to be updated.
        :type task_id: int
        :param project_id: The new project ID to be assigned to the task.
        :type project_id: int
        :return: None
        """
        try:
            task = self._session.query(CXTask).filter(CXTask.id == task_id).first()
            if not task:
                print(f"No task found with ID: {task_id}")
                return
            task.project_id = project_id
            self._session.commit()
            print(f"Updated task ID {task_id} to project ID {project_id}")
        except Exception as e:
            self._session.rollback()
            print(f"Error updating project ID for task {task_id}: {str(e)}")

    def update_task_start_date(self, task_id, new_start_date):
        """
        Updates the start date of a task with the given task ID.
    
        :param task_id: The ID of the task to be updated.
        :type task_id: int
        :param new_start_date: The new start date to assign to the task.
        :type new_start_date: datetime.date
        :return: None
        """
        try:
            task = self._session.query(CXTask).filter(CXTask.id == task_id).first()
            if not task:
                print(f"No task found with ID: {task_id}")
                return
            task.start_date = new_start_date
            self._session.commit()
            print(f"Updated start date for task ID {task_id} to {new_start_date}")
        except Exception as e:
            self._session.rollback()
            print(f"Error updating start date for task {task_id}: {str(e)}")

    def update_task_end_date(self, task_id, new_end_date):
        """
        Updates the end date of a task with the given task ID.
    
        :param task_id: The ID of the task to be updated.
        :type task_id: int
        :param new_end_date: The new end date to assign to the task.
        :type new_end_date: datetime.date
        :return: None
        """
        try:
            task = self._session.query(CXTask).filter(CXTask.id == task_id).first()
            if not task:
                print(f"No task found with ID: {task_id}")
                return
            task.end_date = new_end_date
            self._session.commit()
            print(f"Updated end date for task ID {task_id} to {new_end_date}")
        except Exception as e:
            self._session.rollback()
            print(f"Error updating end date for task {task_id}: {str(e)}")

    def recalculate_task_end_time(self):
        """
        Recalculates and updates the end time for each task based on start_date + duration.
        
        :return: None
        """
        try:
            tasks = self._session.query(CXTask).all()  # Fetch all tasks
            for task in tasks:
                if task.start_date and task.duration:
                    # Calculate new end_date: start_date + duration
                    new_end_date = task.start_date + timedelta(days=task.duration)
                    task.end_date = new_end_date  # Update end_date
            self._session.commit()  # Commit updates to the database
            print("Successfully recalculated end times for all tasks.")
        except Exception as e:
            self._session.rollback()
            print(f"Error recalculating task end times: {str(e)}")
            
            

    def update_task_duration(self, task_id, new_duration):
        """
        Updates the duration of a task with the given task ID.
    
        :param task_id: The ID of the task to be updated.
        :type task_id: int
        :param new_duration: The new duration to assign to the task.
        :type new_duration: int
        :return: None
        """
        try:
            task = self._session.query(CXTask).filter(CXTask.id == task_id).first()
            if not task:
                print(f"No task found with ID: {task_id}")
                return
            task.duration = new_duration
            self._session.commit()
            print(f"Updated duration for task ID {task_id} to {new_duration}")
        except Exception as e:
            self._session.rollback()
            print(f"Error updating duration for task {task_id}: {str(e)}")

    def add_gantt_user_project_view_options(self, project_id, user_id, view_type='PROJECT', zoom_level=None):
        """
        Adds a CXProjectUserSetup row to the table using the passed parameters.
    
        :param project_id: The ID of the project.
        :param user_id: The ID of the user.
        :param view_type: The type of view, default is 'PROJECT'.
        :param zoomLevel: The zoom level, default is None.
        :return: None
        """
        try:
            gantt_setup = CXProjectUserSetup(
                project_id=project_id,
                user_id=user_id,
                view_type=view_type,
                zoom_level=zoom_level
            )
            self._session.add(gantt_setup)
            self._session.commit()
            print(f"Added CXProjectUserSetup row for project ID: {project_id}, user ID: {user_id}")
        except Exception as e:
            self._session.rollback()
            print(f"Error adding CXProjectUserSetup row: {str(e)}")

    def set_task_hierarchy(self, parent_id, child_id):
        """
        Sets up a parent-child relationship between tasks while updating the start and end dates as needed.
    
        :param parent_id: The ID of the parent task.
        :type parent_id: int
        :param child_id: The ID of the child task.
        :type child_id: int
        """
        try:
            parent_task = self._session.query(CXTask).filter(CXTask.id == parent_id).first()
            child_task = self._session.query(CXTask).filter(CXTask.id == child_id).first()

            if not parent_task:
                print(f"Parent task with ID {parent_id} does not exist.")
                return
            if not child_task:
                print(f"Child task with ID {child_id} does not exist.")
                return

            # Update child task to reference parent task
            child_task.parent_id = parent_id

            # Ensure child task does not start before parent task
            if child_task.start_date < parent_task.start_date:
                child_task.start_date = parent_task.start_date

            # Update the parent's end date to match the latest child's end date
            children_tasks = self._session.query(CXTask).filter(CXTask.parent_id == parent_id).all()
            latest_end_date = max(
                [child_task.end_date] + [child.end_date for child in children_tasks if child.end_date is not None]
            )
            parent_task.end_date = latest_end_date

            # Commit changes
            self._session.commit()
            print(f"Task {child_id} is now a child of Task {parent_id}. Parent's end date updated.")
        except Exception as e:
            self._session.rollback()
            print(f"Error setting task hierarchy between {parent_id} and {child_id}: {str(e)}")

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
        task_status_list = ['BLOCKED','BACKLOG','IN_PROGRESS','COMPLETE','CANCELLED','RETIRED','DEFERRED']
        # Create resources
        resource_ids = []
        for i in range(self.nResources):
            resource_name = f"Resource {i + 1}"
            #resource_type = f"Type {i % 5}"  # Assign some example resource types
            resource_type = random.choice(resource_list)

            db_operator.add_resource(name=resource_name, resource_type=resource_type, username='efreeman')
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
            db_operator.add_programme(title=title,
                                      start_date=start_date,
                                      portfolio_id=random.choice(range(len(portfolio_ids)))+1,
                                      owner_id=random.choice(range(len(resource_ids)))+1)
            programme_ids.append(i + 1)  # Collecting dummy IDs for programmes (assuming sequential IDs)

        # Create projects
        project_ids = []
        for i in range(self.nProjects):
            title = f"Project {i + 1}"
            start_date = date.today()
            if random.random() > 0.3:
                db_operator.add_project(title=title,
                                        owner_id=random.choice(range(len(resource_ids)))+1,
                                        start_date=start_date,
                                        programme_id=random.choice(range(len(programme_ids)))+1)
            else:
                db_operator.add_project(title=title,
                                        owner_id=random.choice(range(len(resource_ids)))+1,
                                        start_date=start_date,
                                        portfolio_id=random.choice(range(len(portfolio_ids)))+1)
            project_ids.append(i + 1)  # Collecting dummy IDs for projects (assuming sequential IDs)
            # for resource_id in range(len(resource_ids)):
            #     db_operator.add_project_gantt_permissions(user_id=resource_id+1, project_id=i+1)
            db_operator.add_project_gantt_permissions(user_id=1, project_id=i+1)
            db_operator.add_gantt_user_project_view_options(project_id=i+1, user_id=1, view_type='PROJECT')
            print(f"Added project view per")


        # Create tasks with random start and finish dates
        task_ids = []
        task_hierarchy = {}  # To track parent-child relationships
        task_project_mapping = {}  # To ensure tasks in a chain are in the same project
        for i in range(self.nTasks):
            task_title = f"Task {i + 1}"
            status = random.choice(task_status_list)
            project_id = random.choice(range(len(project_ids))) + 1  # Assign tasks randomly to projects
            start_date = date.today() + timedelta(days=random.randint(0, 30))
            duration = random.choice([i * 0.5 for i in range(1, 21)])
            finish_date = start_date + timedelta(days=duration)  # Ensure finish is after start
            db_operator.add_task(title=task_title, status=status, project_id=project_id, start_date=start_date,
                                 end_date=finish_date)
            task_ids.append(i + 1)  # Collecting dummy IDs for tasks (assuming sequential IDs)
            task_hierarchy[i + 1] = []  # Initialize empty child list
            task_project_mapping[i + 1] = project_id  # Map task to its project
            print(f"Created task: {task_title}, start_date: {start_date}, finish_date: {finish_date}")

            # Assign 1 to 3 random resources to the task
            num_resources = random.randint(1, 3)
            for _ in range(num_resources):
                resource_id = random.choice(range(len(resource_ids))) + 1  # Randomly select resource ID
                db_operator.add_task_resource_link(task_id=i + 1, resource_id=resource_id)
                print(f"Assigned resource ID {resource_id} to task ID {i + 1}")

        # Create random task dependencies
        for task_id in task_ids:
            if random.random() > 0.5:  # 50% chance to create a dependency
                task_project_id = task_project_mapping[task_id]
                same_project_task_ids = [t_id for t_id in task_ids if task_project_mapping[t_id] == task_project_id]

                # Exclude ancestors (parents and parent's parents, etc.) and the task itself
                excluded_tasks = set()
                current_task = task_id
                while current_task in task_hierarchy:
                    excluded_tasks.add(current_task)
                    if not task_hierarchy[current_task]:
                        break
                    current_task = task_hierarchy[current_task][0]
                potential_dependent_tasks = [t_id for t_id in same_project_task_ids if t_id not in excluded_tasks]

                if potential_dependent_tasks:
                    dependent_task_id = random.choice(potential_dependent_tasks)

                    # Check for circular dependency
                    if task_id in task_hierarchy and dependent_task_id in task_hierarchy[task_id]:
                        print(
                            f"Circular dependency detected between Task {task_id} and Task {dependent_task_id}. Skipping.")
                        continue

                    # Set dependent task's project to match the predecessor's project
                    db_operator.update_task_project(dependent_task_id, task_project_id)
                    task_project_mapping[dependent_task_id] = task_project_id  # Update mapping

                    # Ensure dependent task's start date is after the predecessor's end date
                    db_operator.add_task_dependency(predecessor_id=dependent_task_id, successor_id=task_id)
                    task_hierarchy[dependent_task_id].append(task_id)
                    task_start_date = db_operator.get_task_start_date(task_id)
                    predecessor_end_date = db_operator.get_task_end_date(dependent_task_id)
                    if task_start_date <= predecessor_end_date:
                        db_operator.update_task_start_date(task_id, predecessor_end_date + timedelta(days=1))
                    print(f"Task {task_id} now depends on Task {dependent_task_id}")

            elif random.random() > 0.7:  # Additional chance to make tasks parents of others
                task_project_id = task_project_mapping[task_id]
                same_project_task_ids = [t_id for t_id in task_ids if task_project_mapping[t_id] == task_project_id]
                potential_child_tasks = [t_id for t_id in same_project_task_ids if t_id != task_id]

                if potential_child_tasks:
                    child_task_id = random.choice(potential_child_tasks)

                    # Check for circular dependency
                    existing_parents = set()
                    current_child = child_task_id
                    while current_child in task_hierarchy:
                        parents = task_hierarchy[current_child]
                        existing_parents.update(parents)
                        if not parents:
                            break
                        current_child = parents[0]
                    if task_id in existing_parents:
                        print(
                            f"Circular dependency detected while setting Task {task_id} as parent of Task {child_task_id}. Skipping.")
                        continue

                    db_operator.set_task_hierarchy(parent_id=task_id, child_id=child_task_id)
                    task_hierarchy[task_id].append(child_task_id)
                    print(f"Task {task_id} is now a parent of Task {child_task_id}")




            # Recalculate task end date based on start date and duration
            task_start_date = db_operator.get_task_start_date(task_id)
            task_duration = db_operator.get_task_duration(task_id)
            recalculated_end_date = task_start_date + timedelta(days=task_duration)
            db_operator.update_task_end_date(task_id, recalculated_end_date)
            print(f"Recalculated end date for Task {task_id} as {recalculated_end_date}")
            
        
