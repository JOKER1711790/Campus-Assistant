"""
Database models for structured campus data.

These tables cover the core MVP use-cases:
- Timetables
- Bus schedules
- Events / notices
- Faculty directory
"""

from datetime import date, time

from sqlalchemy import Boolean, Date, ForeignKey, Integer, String, Time, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    faculty: Mapped[list["FacultyMember"]] = relationship(back_populates="department")


class FacultyMember(Base):
    __tablename__ = "faculty_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str | None] = mapped_column(String(255), unique=True)
    phone: Mapped[str | None] = mapped_column(String(50))
    room: Mapped[str | None] = mapped_column(String(100))
    designation: Mapped[str | None] = mapped_column(String(255))
    department_id: Mapped[int | None] = mapped_column(ForeignKey("departments.id"))

    department: Mapped[Department | None] = relationship(back_populates="faculty")


class TimetableEntry(Base):
    __tablename__ = "timetable_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    program: Mapped[str] = mapped_column(String(100), index=True)
    semester: Mapped[int] = mapped_column(Integer, index=True)
    section: Mapped[str] = mapped_column(String(10), index=True)
    day_of_week: Mapped[str] = mapped_column(String(10), index=True)  # e.g. MON, TUE
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    course_code: Mapped[str] = mapped_column(String(50))
    course_title: Mapped[str] = mapped_column(String(255))
    room: Mapped[str | None] = mapped_column(String(50))
    faculty_name: Mapped[str | None] = mapped_column(String(255))


class BusRoute(Base):
    __tablename__ = "bus_routes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    route_name: Mapped[str] = mapped_column(String(255), index=True)
    origin: Mapped[str] = mapped_column(String(255))
    destination: Mapped[str] = mapped_column(String(255))
    departure_time: Mapped[time] = mapped_column(Time)
    arrival_time: Mapped[time] = mapped_column(Time)
    days_of_week: Mapped[str] = mapped_column(
        String(50)
    )  # e.g. "MON-FRI", "SAT", "SUN"


class CampusEvent(Base):
    __tablename__ = "campus_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    location: Mapped[str | None] = mapped_column(String(255))
    start_date: Mapped[date] = mapped_column(Date, index=True)
    end_date: Mapped[date | None] = mapped_column(Date)
    is_all_day: Mapped[bool] = mapped_column(Boolean, default=False)


class ExamSchedule(Base):
    __tablename__ = "exam_schedules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    program: Mapped[str] = mapped_column(String(100), index=True)
    semester: Mapped[int] = mapped_column(Integer, index=True)
    course_code: Mapped[str] = mapped_column(String(50), index=True)
    course_title: Mapped[str] = mapped_column(String(255))
    exam_date: Mapped[date] = mapped_column(Date, index=True)
    start_time: Mapped[time] = mapped_column(Time)
    end_time: Mapped[time] = mapped_column(Time)
    room: Mapped[str | None] = mapped_column(String(50))


class FAQ(Base):
    __tablename__ = "faqs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    answer: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str | None] = mapped_column(String(100), index=True)



