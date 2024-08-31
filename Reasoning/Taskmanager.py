from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# from datetime import datetime
import datetime

Base = declarative_base()

class Task(Base):
    __tablename__ = 'tasks'

    task_id = Column(Integer, primary_key=True, autoincrement=True)
    task_description = Column(Text, nullable=False)
    status = Column(String, nullable=False, default='Pending')
    due_date = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    user_id = Column(Integer)  # Optional: Add user association


class TaskManager:
    def __init__(self, db_path='tasks.db'):
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def create_task(self, task_description, due_date=None, user_id=None):
        new_task = Task(task_description=task_description, due_date=due_date, user_id=user_id)
        self.session.add(new_task)
        self.session.commit()
        return new_task.task_id

    def get_task(self, task_id):
        task = self.session.query(Task).filter_by(task_id=task_id).first()
        return task

    def get_all_tasks(self):
        tasks = self.session.query(Task).all()
        return tasks

    def update_task(self, task_id, **kwargs):
        task = self.session.query(Task).filter_by(task_id=task_id).first()
        if task:
            for key, value in kwargs.items():
                setattr(task, key, value)
            self.session.commit()
            return True
        else:
            return False

    def delete_task(self, task_id):
        task = self.session.query(Task).filter_by(task_id=task_id).first()
        if task:
            self.session.delete(task)
            self.session.commit()
            return True
        else:
            return False