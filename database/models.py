from email.policy import default
from enum import unique
from typing import Optional
import re
import typing
import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase, sessionmaker, relationship
from sqlalchemy import CheckConstraint

engine = sa.create_engine("sqlite+pysqlite:///my_db.db", echo=True)
SessionLocal = sessionmaker(bind=engine)

class Base (DeclarativeBase):
    pass

PHONE_REGEX = r"^\+?\d{10,15}$"
EMAIL_REGEX = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

# Таблица с пользователями, при создании записи проверяются на валидность номер телефона и почты,
# Если не валидны то = None
class User(Base):
    __tablename__ = "users"
    user_id = sa.orm.mapped_column(sa.INTEGER, primary_key=True)
    telegram_id = sa.orm.mapped_column(sa.INTEGER, nullable=False, unique=True)
    name = sa.orm.mapped_column(sa.String(30), nullable=False)
    phone = sa.orm.mapped_column(sa.String, nullable=True)
    email = sa.orm.mapped_column(sa.String, nullable=True)
    role = sa.orm.mapped_column(sa.Enum("client", "master", "admin", name="role"),
                                default = 'client', nullable=False)
    created_at = sa.orm.mapped_column(sa.TIMESTAMP, default = sa.func.now(), nullable=False)
    masters = sa.orm.relationship("Master", back_populates="user")
    appointments = sa.orm.relationship("Appointment", back_populates="user")

master_services = sa.Table(
    "master_services", Base.metadata,
    sa.Column('master_id', sa.Integer, sa.ForeignKey('masters.master_id'), primary_key=True),
    sa.Column('service_id', sa.Integer, sa.ForeignKey('services.service_id'), primary_key=True),
)

#Если опыт < 0, то будет выброшена ошибка
class Master(Base):
    __tablename__ = "masters"
    master_id = sa.orm.mapped_column(sa.INTEGER, primary_key=True)
    user_id = sa.orm.mapped_column(sa.INTEGER, sa.ForeignKey("users.user_id"), nullable=False, unique=True)
    user = sa.orm.relationship("User", back_populates="masters")
    specializations = relationship("Service", secondary=master_services, back_populates="masters")
    experience_years = sa.orm.mapped_column(sa.Integer, nullable=False, default=0)
    schedule = sa.orm.relationship(typing.List["Schedule"], back_populates="master")
    appointments = sa.orm.relationship("Appointment", back_populates="master")
    __table_args__ = (CheckConstraint(experience_years >= 0),)

class Service(Base):
    __tablename__ = "services"
    service_id = sa.orm.mapped_column(sa.INTEGER, primary_key=True)
    name = sa.orm.mapped_column(sa.String(30), nullable=False, unique=True)
    description = sa.orm.mapped_column(sa.String, nullable=False)
    price = sa.orm.mapped_column(sa.Integer, nullable=False)
    duration_minutes = sa.orm.mapped_column(sa.Integer, nullable=False)
    masters = sa.orm.relationship("Master", secondary=master_services, back_populates="specializations")
    __table_args__ = (CheckConstraint(duration_minutes >= 0), CheckConstraint(price >= 0))

#фактически таблица рабочих промежутков
class Schedule(Base):
    __tablename__ = "schedules"
    schedule_id = sa.orm.mapped_column(sa.INTEGER, primary_key=True)
    master_id = sa.orm.mapped_column(sa.INTEGER, sa.ForeignKey("masters.master_id"), nullable=False)
    master = sa.orm.relationship("Master", back_populates="schedules")
    work_date = sa.orm.mapped_column(sa.TIMESTAMP,  nullable=False)
    start_time = sa.orm.mapped_column(sa.TIMESTAMP, nullable=False)
    end_time = sa.orm.mapped_column(sa.TIMESTAMP, nullable=False)

class Appointment(Base):
    __tablename__ = "appointments"
    appointment_id = sa.orm.mapped_column(sa.INTEGER, primary_key=True)
    user_id = sa.orm.mapped_column(sa.INTEGER, sa.ForeignKey("users.user_id"))
    master_id = sa.orm.mapped_column(sa.INTEGER, sa.ForeignKey("masters.master_id"))
    service_id = sa.orm.mapped_column(sa.INTEGER, sa.ForeignKey("services.service_id"))
    master = sa.orm.relationship("Master", back_populates="appointments")
    user = sa.orm.relationship("User", back_populates="appointments")
    # !service = sa.orm.relationship("Service", back_populates="appointments")
    start_time = sa.orm.mapped_column(sa.TIMESTAMP, nullable=False)
    end_time = sa.orm.mapped_column(sa.TIMESTAMP, nullable=False)
    status = sa.orm.mapped_column(sa.Enum("confirmed", "cancelled", "pending", name="status"),
                                  default="pending", nullable=False)

class Notification(Base):
    __tablename__ = "notifications"
    notification_id = sa.orm.mapped_column(sa.INTEGER, primary_key=True)
    appointment_id = sa.orm.mapped_column(sa.INTEGER, sa.ForeignKey("appointments.appointment_id"))
    appointment = sa.orm.relationship("Appointment")
    notification_type = sa.orm.mapped_column(sa.Enum("reminder_24h", "reminder_1h", "confirmation", name="notification_type"),)
    sent_at = sa.orm.mapped_column(sa.TIMESTAMP, nullable=False)
    status = sa.orm.mapped_column(sa.Enum("sent", "pending", name="status"), default="pending")

class Statistic(Base):
    __tablename__ = "statistics"
    statistic_id = sa.orm.mapped_column(sa.INTEGER, primary_key=True)
    generated_at = sa.orm.mapped_column(sa.TIMESTAMP, nullable=False)
    total_appointments = sa.orm.mapped_column(sa.Integer, nullable=False)
    cancelled_appointments = sa.orm.mapped_column(sa.Integer, nullable=False)
    revenue = sa.orm.mapped_column(sa.DECIMAL, nullable=False)
    most_popular_service = sa.orm.mapped_column(sa.String, nullable=False)
    busiest_master = sa.orm.mapped_column(sa.String, nullable=False)

Base.metadata.create_all(engine)
