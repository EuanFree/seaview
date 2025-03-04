from db_connect import get_connection

# from sqlalchemy import Column, Integer, String, TIMESTAMP, func, create_engine
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import (create_engine, Column, Integer, String, Date, DateTime,
                        ForeignKey, Enum, Boolean, Double, Table, text)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
import enum
from datetime import datetime





Base = declarative_base()

# Association table for many-to-many relationship between tasks and resources
task_resource_association = Table(
    "task_resource_association", Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id"), primary_key=True),
    Column("resource_id", Integer, ForeignKey("resources.id"), primary_key=True)
)

class ResourceType(enum.Enum):
    """
    Represents different types of resources for classification purposes.

    This enumeration is used to define and differentiate between various types
    of resources that can be utilized in different applications or systems.
    Each member of the enumeration specifies a distinct resource category.

    :ivar PERSON: Represents a resource of type 'Person'.
    :type PERSON: str
    :ivar FACILITY: Represents a resource of type 'Facility'.
    :type FACILITY: str
    :ivar PRODUCT: Represents a resource of type 'Product'.
    :type PRODUCT: str
    :ivar GENERIC: Represents a resource of a general type 'Generic'.
    :type GENERIC: str
    """
    PERSON = "Person"
    FACILITY = "Facility"
    PRODUCT = "Product"
    GENERIC = "Generic"
    
    
class ResourceDepartment(enum.Enum):
    """
    Enumeration of different resource departments.

    Provides a collection of predefined, immutable values that represent
    the various departments involved in organizational operations. This
    class facilitates managing and using department-specific logic or
    configuration in an application.

    :cvar PROGRAMMES: Represents the 'Programme Engineering' department.
    :cvar CORPSERVICES: Represents the 'Corporate Services' department.
    :cvar PRODUCTION: Represents the 'Production' department.
    :cvar AFTERSALES: Represents the 'After Sales' department.
    :cvar STRATBUYING: Represents the 'Strategic Buying' department.
    :cvar LOGISTICS: Represents the 'Logistics' department.
    """
    
    PROGRAMMES = "Programme Engineering"
    CORPSERVICES = "Corporate Services"
    PRODUCTION = "Production"
    AFTERSALES = "After Sales"
    STRATBUYING = "Strategic Buying"
    LOGISTICS = "Logistics"


class CXResource(Base):
    """
    Represents a CX Resource entity within the system.

    The CXResource class corresponds to a table in the database with columns and
    relationships that model a resource entity including attributes for the
    resource's name, type, department, activity status, associated projects,
    portfolios, and weekly working schedule. It also models hierarchical
    relationships such as managers and employees.

    :ivar id: Unique identifier for the resource.
    :type id: int
    :ivar name: Name of the resource.
    :type name: str
    :ivar resource_type: Type of the resource, typically defined by
        the ``ResourceType`` enumeration.
    :type resource_type: ResourceType
    :ivar resource_department: Department associated with the resource,
        defined by the ``ResourceDepartment`` enumeration.
    :type resource_department: ResourceDepartment
    :ivar email: Optional email address of the resource.
    :type email: str
    :ivar is_active: Flag indicating whether the resource is active.
    :type is_active: bool
    :ivar works_on_monday: Indicates if the resource works on Monday.
    :type works_on_monday: bool
    :ivar works_on_tuesday: Indicates if the resource works on Tuesday.
    :type works_on_tuesday: bool
    :ivar works_on_wednesday: Indicates if the resource works on Wednesday.
    :type works_on_wednesday: bool
    :ivar works_on_thursday: Indicates if the resource works on Thursday.
    :type works_on_thursday: bool
    :ivar works_on_friday: Indicates if the resource works on Friday.
    :type works_on_friday: bool
    :ivar works_on_saturday: Indicates if the resource works on Saturday.
    :type works_on_saturday: bool
    :ivar works_on_sunday: Indicates if the resource works on Sunday.
    :type works_on_sunday: bool
    :ivar line_manager_id: ID of the line manager for this resource.
    :type line_manager_id: int
    :ivar line_manager: Relationship to the resource's line manager entity.
    :type line_manager: CXResource
    :ivar employees: List of employees managed by this resource.
    :type employees: list[CXResource]
    :ivar projects: List of ``CXProject`` entities associated with the resource.
    :type projects: list[CXProject]
    :ivar portfolios: List of ``CXPortfolio`` entities associated with the resource.
    :type portfolios: list[CXPortfolio]
    :ivar programmes: List of ``CXProgramme`` entities associated with the resource.
    :type programmes: list[CXProgramme]
    """

    __tablename__ = "resources"
    __table_args__ = {"schema": "seaview"}
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    resource_type = Column(Enum(ResourceType, name="resourcetype", schema="seaview"), nullable=False)
    resource_department = Column(Enum(ResourceDepartment, name="resourcedepartment", schema="seaview"), nullable=False)
    email = Column(String, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    projects = relationship("CXProject", back_populates="owner")
    portfolios = relationship("CXPortfolio", back_populates="owner")
    programmes = relationship("CXProgramme", back_populates="owner")
    #Working pattern
    works_on_monday = Column(Boolean, default=True, nullable=False)
    works_on_tuesday = Column(Boolean, default=True, nullable=False)
    works_on_wednesday = Column(Boolean, default=True, nullable=False)
    works_on_thursday = Column(Boolean, default=True, nullable=False)
    works_on_friday = Column(Boolean, default=False, nullable=False)
    works_on_saturday = Column(Boolean, default=False, nullable=False)
    works_on_sunday = Column(Boolean, default=False, nullable=False)
    
    line_manager_id = Column(Integer, ForeignKey("seaview.resources.id"), nullable=True)
    line_manager = relationship("CXResource", remote_side=[id], back_populates="employees")

    employees = relationship("CXResource", back_populates="line_manager", cascade="all, delete-orphan")


class CXProjectDependencies(Base):
    """

    """
    __tablename__ = "project_dependencies"
    __table_args__ = {"schema": "seaview"}
    predecessor_project_id = Column(Integer, ForeignKey("seaview.projects.id"), primary_key=True)
    successor_project_id = Column(Integer, ForeignKey("seaview.projects.id"), primary_key=True)


class CXPredecessorProgrammeProjectDependencies(Base):
    """

    """
    __tablename__ = "project_programme_dependencies"
    __table_args__ = {"schema": "seaview"}
    successor_project_id = Column(Integer, ForeignKey("seaview.projects.id"), primary_key=True)
    predecessor_programme_id = Column(Integer, ForeignKey("seaview.programmes.id"), primary_key=True)


class CXPredecessorProjectProgrammeDependencies(Base):
    """

    """
    __tablename__ = "programme_project_dependencies"
    __table_args__ = {"schema": "seaview"}
    predecessor_project_id = Column(Integer, ForeignKey("seaview.projects.id"), primary_key=True)
    successor_programme_id = Column(Integer, ForeignKey("seaview.programmes.id"), primary_key=True)


class CXProject(Base):
    """
    Represents a CXProject entity for database mapping.

    This class is used as a SQLAlchemy ORM mapping for the projects table
    in the "seaview" schema. It is designed to manage and represent project
    data within the system, including relationships to owners, tasks, and
    project dependencies such as predecessors and successors.

    :ivar id: The primary key for the project.
    :type id: int
    :ivar title: The title of the project.
    :type title: str
    :ivar start_date: The start date of the project.
    :type start_date: datetime.date

    :ivar owner_id: The foreign key identifying the owner of the project.
    :type owner_id: int
    :ivar is_active: Indicates whether the project is currently active.
    :type is_active: bool
    :ivar owner: The relationship mapping to the project's owner as a
        CXResource object.
    :type owner: CXResource
    :ivar tasks: A collection of tasks associated with the project, mapped
        as CXTask objects.
    :type tasks: list or sqlalchemy.orm.collections.InstrumentedList
    :ivar predecessors: A collection of predecessor projects related to
        this project.
    :type predecessors: list or sqlalchemy.orm.collections.InstrumentedList
    :ivar successors: A collection of successor projects related to this
        project.
    :type successors: list or sqlalchemy.orm.collections.InstrumentedList
    """
    __tablename__ = "projects"
    __table_args__ = {"schema": "seaview"}
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    start_date = Column(Date)
    minimum_date = Column(Date, nullable=True)
    maximum_date = Column(Date, nullable=True)
    owner_id = Column(Integer, ForeignKey("seaview.resources.id"))
    is_active = Column(Boolean, default=True, nullable=False)
    owner = relationship("CXResource", back_populates="projects")
    tasks = relationship("CXTask", back_populates="project")
    portfolio_id = Column(Integer, ForeignKey("seaview.portfolios.id"), nullable=True)
    portfolio = relationship("CXPortfolio", back_populates="projects")
    programme_id = Column(Integer, ForeignKey("seaview.programmes.id"), nullable=True)
    programme = relationship("CXProgramme", back_populates="projects")

    predecessors = relationship(
        "CXProject",
        secondary="seaview.project_dependencies",
        primaryjoin="CXProject.id==CXProjectDependencies.successor_project_id",
        secondaryjoin="CXProject.id==CXProjectDependencies.predecessor_project_id",
        back_populates="successors"
    )

    successors = relationship(
        "CXProject",
        secondary="seaview.project_dependencies",
        primaryjoin="CXProject.id==CXProjectDependencies.predecessor_project_id",
        secondaryjoin="CXProject.id==CXProjectDependencies.successor_project_id",
        back_populates="predecessors"
    )

    programmes_as_predecessors = relationship(
        "CXProgramme",
        secondary="seaview.project_programme_dependencies",
        backref="projects_as_successors"
    )

    programmes_as_successors = relationship(
        "CXProgramme",
        secondary="seaview.programme_project_dependencies",
        backref="projects_as_predecessors"
    )


class CXTaskStatus(enum.Enum):
    """
    Represents the various statuses of a task in the CX system.

    This enumeration defines the possible states a task can be in during its
    lifecycle. It helps in categorizing and managing tasks based on their
    progress and completion stages. The enumeration can be used in systems
    to track and process tasks, ensuring their statuses are well-defined
    and consistent.

    :cvar BLOCKED: Represents a task that is currently blocked and cannot
        proceed until certain conditions are met.
    :type BLOCKED: str
    :cvar BACKLOG: Represents a task that is yet to be started and is in
        the backlog.
    :type BACKLOG: str
    :cvar IN_PROGRESS: Represents a task that is actively being worked on.
    :type IN_PROGRESS: str
    :cvar COMPLETE: Represents a task that has been completed successfully.
    :type COMPLETE: str
    """
    BLOCKED = "Blocked"
    BACKLOG = "Backlog"
    IN_PROGRESS = "InProgress"
    COMPLETE = "Complete"

class CXTaskDependencies(Base):
    """

    """
    __tablename__ = "task_dependencies"
    __table_args__ = {"schema": "seaview"}
    predecessor_id = Column(Integer, ForeignKey("seaview.tasks.id"), primary_key=True)
    successor_id = Column(Integer, ForeignKey("seaview.tasks.id"), primary_key=True)


class CXTask(Base):
    """
    Represents a task entity in the database with attributes related to task details, relationships,
    and overall progress tracking.

    This class models the structure of a task, providing fields for its title, status, project
    association, and relationships with predecessor and successor tasks. It also tracks various
    aspects such as task duration, start and end dates, activity status, and progress percentage.
    These attributes facilitate the management and organization of tasks in the associated
    project schema.

    :ivar id: The unique identifier for the task.
    :type id: int
    :ivar title: The title or name of the task.
    :type title: str
    :ivar status: The status of the task, defined by the CXTaskStatus enumeration.
    :type status: CXTaskStatus
    :ivar project_id: The identifier of the project related to this task.
    :type project_id: int
    :ivar is_active: Indicates whether the task is currently active.
    :type is_active: bool
    :ivar start_date: The starting date of the task.
    :type start_date: datetime.date
    :ivar duration: The duration of the task in days.
    :type duration: float
    :ivar end_date: The ending date of the task.
    :type end_date: datetime.date
    :ivar progress: The completion progress of the task as a percentage.
    :type progress: float
    :ivar predecessors: List of predecessor tasks that must be completed before this task.
    :type predecessors: List[CXTask]

    :ivar project: The project associated with this task.
    :type project: CXProject
    """
    __tablename__ = "tasks"
    __table_args__ = {"schema": "seaview"}
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    status = Column(Enum(CXTaskStatus, name="status", schema="seaview"), nullable=False)
    project_id = Column(Integer, ForeignKey("seaview.projects.id"))
    is_active = Column(Boolean, default=True, nullable=False)
    start_date = Column(Date)
    duration = Column(Double, default=1.0)
    end_date = Column(Date)
    progress = Column(Double, default=0.0)

    predecessors = relationship("CXTask",
                                secondary="seaview.task_dependencies",
                                primaryjoin="CXTask.id==CXTaskDependencies.successor_id",
                                secondaryjoin="CXTask.id==CXTaskDependencies.predecessor_id",
                                backref="successors")

    project = relationship("CXProject", back_populates="tasks")


class CXPortfolio(Base):
    """
    Represents a portfolio entity in the database.

    This class maps to the "portfolios" table in the "seaview" schema. It defines the
    portfolio's attributes, including its title, objective, start date, owner, and
    its relationships with other entities such as resources, projects, and programs.

    :ivar id: Unique identifier for the portfolio.
    :type id: int
    :ivar title: Title of the portfolio. This is required and cannot be null.
    :type title: str
    :ivar goal: The primary goal or objective associated with the portfolio.
    :type goal: str
    :ivar start_date: The start date of the portfolio.
    :type start_date: datetime.date
    :ivar owner_id: Foreign key reference to the ID of the resource that owns the portfolio.
    :type owner_id: int
    :ivar is_active: Indicates whether the portfolio is active. Defaults to True.
    :type is_active: bool
    :ivar owner: Relationship to the CXResource entity, representing the owner
                 of this portfolio.
    :type owner: CXResource
    :ivar projects: Relationship to CXProject entities associated with the portfolio.
    :type projects: List[CXProject]
    :ivar programmes: Relationship to CXProgramme entities associated with the portfolio.
    :type programmes: List[CXProgramme]
    """
    __tablename__ = "portfolios"
    __table_args__ = {"schema": "seaview"}
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    goal = Column(String)
    start_date = Column(Date)
    owner_id = Column(Integer, ForeignKey("seaview.resources.id"))
    is_active = Column(Boolean, default=True, nullable=False)

    owner = relationship("CXResource", back_populates="portfolios")
    projects = relationship("CXProject")
    programmes = relationship("CXProgramme")


class CXProgramme(Base):
    """
    Represents a programme entity in the database.

    This class maps to the "programmes" table within the "seaview" schema
    and encapsulates attributes and relationships for a programme. It is
    used for managing programme data, including title, start date, ownership,
    and related projects.

    :ivar id: Unique identifier for the programme.
    :type id: int
    :ivar title: Title of the programme.
    :type title: str
    :ivar start_date: The start date of the programme.
    :type start_date: datetime.date
    :ivar owner_id: Foreign key referencing the owner of the programme.
    :type owner_id: int
    :ivar is_active: Boolean indicating whether the programme is active.
    :type is_active: bool
    :ivar owner: Relationship to the CXResource entity representing
        the owner of the programme.
    :type owner: CXResource
    :ivar projects: Relationship to associated `CXProject` entities.
    :type projects: list[CXProject]
    """
    __tablename__ = "programmes"
    __table_args__ = {"schema": "seaview"}
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    start_date = Column(Date)
    owner_id = Column(Integer, ForeignKey("seaview.resources.id"))
    is_active = Column(Boolean, default=True, nullable=False)
    owner = relationship("CXResource", back_populates="programmes")
    projects = relationship("CXProject")
    portfolio_id = Column(Integer, ForeignKey("seaview.portfolios.id"), nullable=True)
    portfolio = relationship("CXPortfolio", back_populates="programmes")

class CXTaskChange(Base):
    """
    Represents a record of changes made to a task in the system.

    This class is designed to capture and store changes made to tasks, tracking details such as
    the who made the changes, when the changes occurred, as well as details of the old and new
    values. It links to both the task being modified and the resource making the change through
    relationships, ensuring data consistency and enabling detailed change tracking.

    :ivar id: A unique identifier for the change record.
    :type id: int
    :ivar task_id: The identifier of the task associated with this change.
    :type task_id: int
    :ivar change_date: The timestamp of when the change was made. Defaults to the current UTC time.
    :type change_date: datetime
    :ivar changed_by: The identifier of the resource (user) who made the change.
    :type changed_by: int
    :ivar old_values_json: JSON string containing the old values before the change. May be empty.
    :type old_values_json: str
    :ivar new_value_json: JSON string containing the new values after the change. May be empty.
    :type new_value_json: str
    :ivar task: A relationship linking this change to the associated task.
    :type task: CXTask
    :ivar changer: A relationship linking this change to the resource that made it.
    :type changer: CXResource
    """
    __tablename__ = "task_changes"
    __table_args__ = {"schema": "seaview"}
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("seaview.tasks.id"), nullable=False)
    change_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    changed_by = Column(Integer, ForeignKey("seaview.resources.id"), nullable=False)
    old_values_json = Column(String)
    new_value_json = Column(String)
    task = relationship("CXTask", back_populates="changes")
    changer = relationship("CXResource")
    # Add reverse relationship in the CXTask class
    CXTask.changes = relationship("CXTaskChange", back_populates="task", cascade="all, delete-orphan")

class CXProjectGanttPermissions(Base):
    """
    Represents the permissions for project Gantt resources in the system.

    This class maps to the `gantt_permissions_store` table in the `seaview` schema.
    It is used to define and manage various permissions associated with users and
    projects in a Gantt charting context. Permissions specified in this class
    determine what operations a user can perform on project-linked Gantt resources.

    :ivar user_id: The ID of the user associated with these permissions.
    :type user_id: int
    :ivar project_id: The ID of the project to which these permissions apply.
    :type project_id: int
    :ivar write_permission: Indicates whether the user has permission to write or
        modify the Gantt resource.
    :type write_permission: bool
    :ivar add_permission: Indicates whether the user has permission to add new
        elements to the Gantt resource.
    :type add_permission: bool
    :ivar write_on_parent_permission: Specifies if the user can write to or modify
        the parent resource of the Gantt project.
    :type write_on_parent_permission: bool
    :ivar cannot_close_task_if_issue_open_permission: Determines whether the user
        cannot close a task if there are unresolved issues related to it.
    :type cannot_close_task_if_issue_open_permission: bool
    :ivar can_add_permission: Specifies if the user has explicit permission to add
        resources to the Gantt project.
    :type can_add_permission: bool
    :ivar can_delete_permission: Indicates whether the user has permission to
        delete elements from the Gantt resource.
    :type can_delete_permission: bool
    """
    __tablename__ = "gantt_permissions_store"
    __table_args__ = {"schema": "seaview"}
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("seaview.resources.id"))
    project_id = Column(Integer, ForeignKey("seaview.projects.id"))
    write_permission = Column(Boolean, default=True, nullable=False)
    add_permission = Column(Boolean, default=True, nullable=False)
    write_on_parent_permission = Column(Boolean, default=True, nullable=False)
    cannot_close_task_if_issue_open_permission = Column(Boolean, default=True, nullable=False)
    can_add_permission = Column(Boolean, default=True, nullable=False)
    can_delete_permission = Column(Boolean, default=True, nullable=False)

class CXProjectTaskUserSetup(Base):
    """
    Representation of user-specific settings for viewing project tasks in a Gantt chart.

    This class is a model that maps to the database table
    "gantt_user_project_tasks_view_options" under the schema "seaview". It is
    used to store and retrieve user-specific settings related to how project
    tasks are displayed in a Gantt chart. The settings include information
    such as whether a task in a given project is collapsed for a specific user.

    :ivar user_id: Unique identifier of the user associated with these settings.
    :type user_id: int
    :ivar project_id: Unique identifier of the project associated with the task.
    :type project_id: int
    :ivar task_id: Unique identifier of the task associated with the settings.
    :type task_id: int
    :ivar collapsed: Indicates whether the task display is collapsed
        for the associated user and project. Default is False.
    :type collapsed: bool
    """
    __tablename__ = "gantt_user_project_tasks_view_options"
    __table_args__ = {"schema": "seaview"}
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("seaview.resources.id"))
    project_id = Column(Integer, ForeignKey("seaview.projects.id"))
    task_id = Column(Integer, ForeignKey("seaview.tasks.id"))
    collapsed = Column(Boolean, default=False, nullable=False)

class CXViewType(enum.Enum):
    """
    Enumeration representing types of views in the system for entities like portfolios, programmes, or projects.

    :cvar PORTFOLIO: Represents a view for portfolios.
    :type PORTFOLIO: int
    :cvar PROGRAMME: Represents a view for programmes.
    :type PROGRAMME: int
    :cvar PROJECT: Represents a view for projects.
    :type PROJECT: int
    """
    PORTFOLIO = 0
    PROGRAMME = 1
    PROJECT = 2


# class CXProjectDependencies(Base):
#     """
#     Represents the dependencies between projects in the system.
#
#     This class serves as a linkage table that captures and stores relationships
#     between predecessor and successor projects in the "seaview" schema. It enables
#     the system to model project dependencies, allowing complex project workflows
#     to be outlined clearly.
#
#     :ivar id: A unique identifier for the dependency record.
#     :type id: int
#     :ivar predecessor_project_id: The identifier of the predecessor project in the dependency.
#     :type predecessor_project_id: int
#     :ivar successor_project_id: The identifier of the successor project in the dependency.
#     :type successor_project_id: int
#     :ivar predecessor_project: The project entity serving as the predecessor in the dependency.
#     :type predecessor_project: CXProject
#     :ivar successor_project: The project entity serving as the successor in the dependency.
#     :type successor_project: CXProject
#     """
#     __tablename__ = "project_dependencies"
#     __table_args__ = {"schema": "seaview"}
#
#     id = Column(Integer, primary_key=True)
#     predecessor_project_id = Column(Integer, ForeignKey("seaview.projects.id"), nullable=False)
#     successor_project_id = Column(Integer, ForeignKey("seaview.projects.id"), nullable=False)
#
#     predecessor_project = relationship("CXProject", foreign_keys=[predecessor_project_id], back_populates="successors")
#     successor_project = relationship("CXProject", foreign_keys=[successor_project_id], back_populates="predecessors")


class CXProjectUserSetup(Base):
    """
    Represents a user's project view options, including preferences for zoom level and start date.

    Provides a mapping of user-specific configurations for project views in a gantt chart system.
    The table includes associations to users and projects and stores personalized settings.

    :ivar __tablename__: Table name in the database.
    :type __tablename__: str
    :ivar __table_args__: Additional table configuration options.
    :type __table_args__: dict
    :ivar user_id: Foreign key linking to the user's resource ID.
    :type user_id: int
    :ivar project_id: Foreign key linking to the associated project's ID.
    :type project_id: int
    :ivar zoom_level: The user's preferred zoom level for the gantt chart view.
    :type zoom_level: str
    :ivar start_date: The user's preferred start date for viewing the project.
    :type start_date: datetime.date
    """
    __tablename__ = "gantt_user_project_view_options"
    __table_args__ = {"schema": "seaview"}
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("seaview.resources.id"))
    view_type = Column(Enum(CXViewType, name="view_type", schema="seaview"), default=CXViewType.PROJECT)
    project_id = Column(Integer, ForeignKey("seaview.projects.id"))
    zoom_level = Column(String)
    start_date = Column(Date)


# Grant read/write access to a specific user for the seaview schema
def grant_user_access(engine, user):
    """
    Grants read and write access to a specific user for the seaview schema.
    
    :param engine: SQLAlchemy Engine instance to connect to the database.
    :param user: The database username to which access will be granted.
    :return: None
    """
    with engine.connect() as conn:
        conn.execute(text(f"GRANT USAGE ON SCHEMA seaview TO {user}"))
        conn.execute(text(f"GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA seaview TO {user}"))
        conn.execute(text(
            f"ALTER DEFAULT PRIVILEGES IN SCHEMA seaview GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {user}"))
        conn.commit()

# To generate the SQL for the defined model:
def generate_sql(db_config):
    """
    Generates and prints the SQL definition of the defined schema and tables.

    :return: None
    """
    engine = create_engine('postgresql+psycopg2://'
                           +db_config["user"]+':'
                           +db_config["password"]+'@'
                           +db_config["host"]+'/'
                           +db_config["dbname"])

    # Create the schema if it doesn't exist
    with engine.connect() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS seaview"))
        conn.commit()

    grant_user_access(engine, 'nt_client')

    # Set schema for metadata
    Base.metadata.schema = "seaview"
    Base.metadata.create_all(engine)
    print("\n".join(str(table) for table in Base.metadata.tables.values()))
