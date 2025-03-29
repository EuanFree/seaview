from db_connect import get_connection

from sqlalchemy import (create_engine, Column, Integer, String, Date, DateTime,
                        ForeignKey, Enum, Boolean, Double, Table, text)
from sqlalchemy.orm import declarative_base, relationship, sessionmaker, registry
import enum
from datetime import datetime

Base = declarative_base()

class CXTaskResourceAssociation(Base):
    __tablename__ = "task_resource_association"
    __table_args__ = {"schema": "seaview"}
    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, ForeignKey("seaview.tasks.id"))
    resource_id = Column(Integer, ForeignKey("seaview.resources.id"))

class CXProjectDependencyAssociation(Base):
    __tablename__ = "project_dependency_association"
    __table_args__ = {"schema": "seaview"}
    id = Column(Integer, primary_key=True)
    predecessor_project_id = Column(Integer, ForeignKey("seaview.projects.id"), nullable=True)
    predecessor_programme_id = Column(Integer, ForeignKey("seaview.programmes.id"), nullable=True)
    successor_project_id = Column(Integer, ForeignKey("seaview.projects.id"))

class CXProgrammeDependencyAssociation(Base):
    __tablename__ = "programme_dependency_association"
    __table_args__ = {"schema": "seaview"}
    id = Column(Integer, primary_key=True)
    predecessor_programme_id = Column(Integer, ForeignKey("seaview.programmes.id"), nullable=True)
    predecessor_project_id = Column(Integer, ForeignKey("seaview.projects.id"), nullable=True)
    successor_programme_id = Column(Integer, ForeignKey("seaview.programmes.id"))


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
    resource_department = Column(Enum(ResourceDepartment, name="resourcedepartment", schema="seaview"), nullable=True)
    email = Column(String, nullable=True)
    username = Column(String, nullable=True)
    is_active = Column(Boolean, server_default="true", nullable=False)
    projects = relationship("CXProject", back_populates="owner")
    portfolios = relationship("CXPortfolio", back_populates="owner")
    programmes = relationship("CXProgramme", back_populates="owner")
    #Working pattern
    works_on_monday = Column(Boolean, server_default="true", nullable=False)
    works_on_tuesday = Column(Boolean, server_default="true", nullable=False)
    works_on_wednesday = Column(Boolean, server_default="true", nullable=False)
    works_on_thursday = Column(Boolean, server_default="true", nullable=False)
    works_on_friday = Column(Boolean, server_default="false", nullable=False)
    works_on_saturday = Column(Boolean, server_default="false", nullable=False)
    works_on_sunday = Column(Boolean, server_default="false", nullable=False)


class CXManagerEmployeeAssociation(Base):
    """
    Represents the association between managers and employees.

    This class defines a table to store the relationships between managers
    and employees within the "seaview" schema. Each association links a manager
    to an employee using their respective resource IDs as foreign keys.

    :ivar __tablename__: Name of the table in the database.
    :type __tablename__: str
    :ivar __table_args__: Specification of the schema where the table resides.
    :type __table_args__: dict
    :ivar manager: Resource ID of the manager (foreign key reference).
    :type manager: int
    :ivar employee: Resource ID of the employee (foreign key reference).
    :type employee: int
    """
    __tablename__ = "manager_employee_associations"
    __table_args__ = {"schema": "seaview"}
    manager = Column(Integer, ForeignKey("seaview.resources.id"), primary_key=True)
    employee = Column(Integer, ForeignKey("seaview.resources.id"), primary_key=True)


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
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    duration = Column(Double)
    owner_id = Column(Integer, ForeignKey("seaview.resources.id"))
    is_active = Column(Boolean, server_default="true", nullable=False)
    overall_budget = Column(Double, default=0.0)
    owner = relationship("CXResource", back_populates="projects", single_parent=True)
    tasks = relationship("CXTask", back_populates="project")
    portfolio_id = Column(Integer, ForeignKey("seaview.portfolios.id"), nullable=True)
    portfolio = relationship("CXPortfolio", back_populates="projects")
    programme_id = Column(Integer, ForeignKey("seaview.programmes.id"), nullable=True)
    programme = relationship("CXProgramme", back_populates="projects")


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
    CANCELLED = "Cancelled"
    RETIRED = "Retired"
    DEFERRED = "Deferred"


class CXTaskDependencies(Base):
    """
    Representation of task dependencies in the system.

    This class is used to define the relationship between tasks, specifying
    which task is a predecessor and which is a successor. It serves as a
    mapping table for establishing dependencies between tasks within a
    specific database schema. This relationship is defined within the
    `seaview` schema and enforces a many-to-many relationship between tasks.

    :ivar __tablename__: Name of the table in the database.
    :type __tablename__: str
    :ivar __table_args__: Additional arguments specifying schema information for the table.
    :type __table_args__: dict
    :ivar predecessor_id: Identifier for the predecessor task in the dependency relationship.
    :type predecessor_id: int
    :ivar successor_id: Identifier for the successor task in the dependency relationship.
    :type successor_id: int
    """
    __tablename__ = "task_dependencies"
    __table_args__ = {"schema": "seaview"}
    predecessor_id = Column(Integer, ForeignKey("seaview.tasks.id"), primary_key=True)
    successor_id = Column(Integer, ForeignKey("seaview.tasks.id"), primary_key=True)
    lag = Column(Double, default=0)




class CXTask(Base):
    """
    Represents a task in the system.

    The CXTask class defines the structure of a task entity within the application. This includes task-specific
    attributes such as title, status, associated project, and other related properties. It utilizes SQLAlchemy for
    ORM functionality and interacts with other entities like CXProject to establish relationships. The class is
    designed to capture all relevant details about a task for effective tracking and management in the system.

    :ivar id: Unique identifier for the task.
    :type id: int
    :ivar title: Title or name of the task.
    :type title: str
    :ivar status: Current status of the task. Defined as an Enum of CXTaskStatus.
    :type status: CXTaskStatus
    :ivar project_id: Reference to the project this task is part of.
    :type project_id: int or None
    :ivar is_active: Indicates whether the task is active.
    :type is_active: bool
    :ivar start_date: Scheduled start date of the task.
    :type start_date: datetime.date or None
    :ivar duration: Duration of the task, in days.
    :type duration: float
    :ivar end_date: Scheduled end date of the task.
    :type end_date: datetime.date or None
    :ivar progress: Progress percentage of the task.
    :type progress: float
    :ivar project: Relationship that links this task to its associated project (CXProject).
    :type project: CXProject or None
    """
    __tablename__ = "tasks"
    __table_args__ = {"schema": "seaview"}
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    status = Column(Enum(CXTaskStatus, name="status", schema="seaview"), nullable=False)
    project_id = Column(Integer, ForeignKey("seaview.projects.id"))
    is_active = Column(Boolean, server_default="true", nullable=False)
    start_date = Column(DateTime)
    duration = Column(Double, default=1.0)
    end_date = Column(DateTime)
    progress = Column(Double, default=0.0)
    parent_id = Column(Integer, ForeignKey("seaview.tasks.id"), nullable=True)
    budget = Column(Double, default=0.0)
    spend = Column(Double, default=0.0)
    project = relationship("CXProject", back_populates="tasks")
    changes = relationship('CXTaskChange', back_populates="task")

    # children = relationship("CXTask", back_populates="parent", cascade="all, delete-orphan")


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
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    duration = Column(Double)
    owner_id = Column(Integer, ForeignKey("seaview.resources.id"))
    is_active = Column(Boolean, server_default="true", nullable=False)

    owner = relationship("CXResource", back_populates="portfolios", cascade="all, delete-orphan", single_parent=True)
    projects = relationship("CXProject", back_populates="portfolio", cascade="all, delete-orphan")
    programmes = relationship("CXProgramme", back_populates="portfolio", cascade="all, delete-orphan")


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
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    duration = Column(Double)
    owner_id = Column(Integer, ForeignKey("seaview.resources.id"))
    is_active = Column(Boolean, server_default="true", nullable=False)
    overall_budget = Column(Double, default=0.0)
    owner = relationship("CXResource", back_populates="programmes", cascade="all", single_parent=True)
    projects = relationship("CXProject", back_populates="programme", cascade="all, delete-orphan")
    portfolio_id = Column(Integer, ForeignKey("seaview.portfolios.id"), nullable=True)
    portfolio = relationship("CXPortfolio", back_populates="programmes", cascade="all")

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
    write_permission = Column(Boolean, server_default="true", nullable=False)
    add_permission = Column(Boolean, server_default="true", nullable=False)
    write_on_parent_permission = Column(Boolean, server_default="true", nullable=False)
    cannot_close_task_if_issue_open_permission = Column(Boolean, server_default="true", nullable=False)
    can_add_permission = Column(Boolean, server_default="true", nullable=False)
    can_delete_permission = Column(Boolean, server_default="true", nullable=False)

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
    collapsed = Column(Boolean, server_default="false", nullable=False)

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


class CXProjectZoomLevels(enum.Enum):
    """
    Enumeration representing different time intervals.

    This Enum is used to define a set of constant values, representing specific
    time intervals that may be used in a broader context, such as filtering or
    categorizing data by these periods.

    :ivar DAYS3: Represents a 3-day time interval.
    :type DAYS3: str
    :ivar WEEK1: Represents a 1-week time interval.
    :type WEEK1: str
    :ivar WEEK2: Represents a 2-week time interval.
    :type WEEK2: str
    :ivar MONTH1: Represents a 1-month time interval.
    :type MONTH1: str
    :ivar QUARTER1: Represents a 1-quarter (3 months) time interval.
    :type QUARTER1: str
    :ivar QUARTER2: Represents a 2-quarter (6 months) time interval.
    :type QUARTER2: str
    :ivar YEAR1: Represents a 1-year time interval.
    :type YEAR1: str
    :ivar YEAR2: Represents a 2-year time interval.
    :type YEAR2: str
    """
    DAYS3 = "3d"
    WEEK1 = "1w"
    WEEK2 = "2w"
    MONTH1 = "1M"
    QUARTER1 = "1Q"
    QUARTER2 = "2Q"
    YEAR1 = "1y"
    YEAR2 = "2y"

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
    zoom_level = Column(Enum(CXProjectZoomLevels, name="zoom_level", schema="seaview"), server_default="MONTH1", default=CXProjectZoomLevels.MONTH1)
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
    # Manually order table creation to prevent dependency issues
    # for table in [CXResource, CXPortfolio, CXProgramme, CXProject, CXTask,
    #               CXTaskDependencies, CXProjectDependencies,
    #               CXPredecessorProgrammeProjectDependencies, CXPredecessorProjectProgrammeDependencies]:
    #     table.__table__.create(bind=engine, checkfirst=True)

    Base.registry.configure()
    print("\n".join(str(table) for table in Base.metadata.tables.values()))

