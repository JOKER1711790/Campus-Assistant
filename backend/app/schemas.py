"""
Pydantic models (schemas) used for request/response payloads.
"""

from datetime import date, time
from typing import Optional

from pydantic import BaseModel, Field


class DepartmentOut(BaseModel):
    id: int
    name: str
    code: str

    class Config:
        orm_mode = True


class FacultyMemberOut(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    room: Optional[str] = None
    designation: Optional[str] = None
    department: Optional[DepartmentOut] = None

    class Config:
        orm_mode = True


class TimetableEntryOut(BaseModel):
    id: int
    program: str
    semester: int
    section: str
    day_of_week: str
    start_time: time
    end_time: time
    course_code: str
    course_title: str
    room: Optional[str] = None
    faculty_name: Optional[str] = None

    class Config:
        orm_mode = True


class BusRouteOut(BaseModel):
    id: int
    route_name: str
    origin: str
    destination: str
    departure_time: time
    arrival_time: time
    days_of_week: str

    class Config:
        orm_mode = True


class CampusEventOut(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    location: Optional[str] = None
    start_date: date
    end_date: Optional[date] = None
    is_all_day: bool

    class Config:
        orm_mode = True


class ExamScheduleOut(BaseModel):
    id: int
    program: str
    semester: int
    course_code: str
    course_title: str
    exam_date: date
    start_time: time
    end_time: time
    room: Optional[str] = None

    class Config:
        orm_mode = True


class FAQOut(BaseModel):
    id: int
    question: str
    answer: str
    category: Optional[str] = None

    class Config:
        orm_mode = True


class ChatRequest(BaseModel):
    message: str = Field(..., description="Student's natural language query")
    user_id: Optional[str] = Field(
        default=None, description="Optional identifier for personalization"
    )


class ChatResponse(BaseModel):
    answer: str
    intent: str
    # Optional structured payloads that frontend can render nicely
    timetable: list[TimetableEntryOut] | None = None
    bus_routes: list[BusRouteOut] | None = None
    events: list[CampusEventOut] | None = None
    exams: list[ExamScheduleOut] | None = None
    faqs: list[FAQOut] | None = None



