from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Table
from sqlalchemy.orm import relationship
from app.database import Base

# Association table for many-to-many relationship between User and Group
user_group = Table(
    "user_group",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("group_id", Integer, ForeignKey("groups.id", ondelete="CASCADE"), primary_key=True),
)


class User(Base):
    """
    Represents a user in the system.

    Attributes:
        id (int): Primary key, unique identifier for the user.
        username (str): Unique username for authentication.
        password_hash (str): Placeholder for the user's password hash.
        goal (int): Personal goal (e.g., number of tasks to complete).
        tasks (List[Task]): One-to-many relationship with Task.
        groups (List[Group]): Many-to-many relationship with Group.
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    goal = Column(Integer, default=1)

    tasks = relationship("Task", back_populates="user", cascade="all, delete-orphan")
    groups = relationship("Group", secondary=user_group, back_populates="members")


class Group(Base):
    """
    Represents a group of users with a shared task goal.

    Attributes:
        id (int): Primary key, unique identifier for the group.
        name (str): Unique name of the group.
        goal (int): Shared task completion goal for the group.
        members (List[User]): Users who are part of the group.
        tasks (List[Task]): Tasks assigned to this group.
    """
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    goal = Column(Integer, default=3)

    members = relationship("User", secondary=user_group, back_populates="groups")
    tasks = relationship("Task", back_populates="group", cascade="all, delete-orphan")


class Task(Base):
    """
    Represents a task that can be assigned to a user or a group.

    Attributes:
        id (int): Primary key, unique identifier for the task.
        title (str): Description or title of the task.
        completed (bool): Flag indicating whether the task is done.
        user_id (int): Foreign key to the user who owns the task.
        group_id (int): Optional foreign key to the group the task belongs to.
        user (User): Relationship to the owning user.
        group (Group): Relationship to the associated group, if any.
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    completed = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=True)

    user = relationship("User", back_populates="tasks")
    group = relationship("Group", back_populates="tasks")


class Plant:
    pass