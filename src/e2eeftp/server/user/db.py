from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker
import os
import uuid


def generate_secure_filename(user_name: str) -> uuid.UUID:
    """Generate a unique folder name.

    Args:
        user_name (str): The user name of the folder.

    Returns:
        UUID: The unique folder name.
    """
    unique_folder_id = uuid.uuid4()
    return unique_folder_id


engine = create_engine("sqlite:///users.db", echo=True)  # echo=True prints the generated SQL to your console
Base = declarative_base()


class Users(Base):
    __tablename__ = "users" 

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(50), nullable=False)
    folder = Column(String(50 + 36), nullable=False)

Base.metadata.create_all(engine)
