"""
Core API routes for the Smart Campus Assistant.

Endpoints:
- `/health` – health check
- `/timetable` – list timetable entries with simple filters
- `/bus_schedule` – list bus routes
- `/events` – list campus events
- `/faculty_directory` – list faculty members
- `/chat` – chatbot endpoint (RAG + simple intent detection)
"""

from datetime import datetime
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .. import models, schemas
from ..db import get_db
from ..rag import generate_answer


router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/timetable", response_model=List[schemas.TimetableEntryOut])
async def get_timetable(
    program: Optional[str] = None,
    semester: Optional[int] = None,
    section: Optional[str] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
):
    stmt = select(models.TimetableEntry)
    if program:
        stmt = stmt.where(models.TimetableEntry.program == program)
    if semester is not None:
        stmt = stmt.where(models.TimetableEntry.semester == semester)
    if section:
        stmt = stmt.where(models.TimetableEntry.section == section)

    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/bus_schedule", response_model=List[schemas.BusRouteOut])
async def get_bus_schedule(
    route_name: Optional[str] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
):
    stmt = select(models.BusRoute)
    if route_name:
        stmt = stmt.where(models.BusRoute.route_name == route_name)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/events", response_model=List[schemas.CampusEventOut])
async def get_events(
    upcoming_only: bool = Query(True, description="Return only current or future events"),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
):
    from datetime import date

    stmt = select(models.CampusEvent)
    if upcoming_only:
        today = date.today()
        stmt = stmt.where(models.CampusEvent.end_date >= today)
    result = await db.execute(stmt)
    return list(result.scalars().all())


@router.get("/faculty_directory", response_model=List[schemas.FacultyMemberOut])
async def get_faculty_directory(
    department_code: Optional[str] = None,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
):
    stmt = select(models.FacultyMember).join(models.Department, isouter=True)
    if department_code:
        stmt = stmt.where(models.Department.code == department_code)
    result = await db.execute(stmt)
    return list(result.scalars().unique().all())


def _classify_intent(message: str) -> str:
    """
    Very naive keyword-based intent classifier for the MVP.

    Replace this later with a small intent-classification model or
    an LLM-based classifier.
    """

    text = message.lower()
    if any(k in text for k in ["timetable", "class time", "schedule"]):
        return "timetable_query"
    if any(k in text for k in ["bus", "shuttle"]):
        return "bus_schedule_query"
    if any(k in text for k in ["event", "fest", "hackathon"]):
        return "events_query"
    if any(k in text for k in ["exam", "midterm", "final"]):
        return "exam_schedule_query"
    if any(k in text for k in ["faculty", "professor", "teacher", "hod"]):
        return "faculty_directory_query"
    if any(k in text for k in ["faq", "how do i", "where can i"]):
        return "faq_query"
    return "general_query"


@router.post("/chat", response_model=schemas.ChatResponse)
async def chat(
    payload: schemas.ChatRequest,
    db: Annotated[AsyncSession, Depends(get_db)] = None,
):
    intent = _classify_intent(payload.message)
    message_lower = payload.message.lower()

    # For timetable queries, skip RAG and return only structured data
    if intent == "timetable_query":
        # Check if query mentions "today"
        is_today = "today" in message_lower or "todays" in message_lower
        
        stmt = select(models.TimetableEntry)
        
        if is_today:
            # Get today's day of week (MON, TUE, etc.)
            today = datetime.now()
            day_name = today.strftime("%a").upper()  # MON, TUE, WED, etc.
            stmt = stmt.where(models.TimetableEntry.day_of_week == day_name)
        
        stmt = stmt.limit(20)
        result = await db.execute(stmt)
        rows = list(result.scalars().all())
        timetable = [
            schemas.TimetableEntryOut.model_validate(r, from_attributes=True)
            for r in rows
        ]
        
        # Simple answer for timetable queries - just the table will show details
        if is_today:
            answer = f"Here's your timetable for today ({day_name}):"
        else:
            answer = "Here's your timetable:"
        
        return schemas.ChatResponse(
            answer=answer,
            intent=intent,
            timetable=timetable,
            bus_routes=None,
            events=None,
            exams=None,
            faqs=None,
        )

    # For structured queries (bus, events, exams), skip RAG and return only data
    if intent == "bus_schedule_query":
        result = await db.execute(select(models.BusRoute).limit(20))
        rows = list(result.scalars().all())
        bus_routes = [
            schemas.BusRouteOut.model_validate(r, from_attributes=True) for r in rows
        ]
        return schemas.ChatResponse(
            answer="Here are the bus schedules:",
            intent=intent,
            timetable=None,
            bus_routes=bus_routes,
            events=None,
            exams=None,
            faqs=None,
        )
    
    elif intent == "events_query":
        result = await db.execute(select(models.CampusEvent).limit(20))
        rows = list(result.scalars().all())
        events = [
            schemas.CampusEventOut.model_validate(r, from_attributes=True)
            for r in rows
        ]
        return schemas.ChatResponse(
            answer="Here are upcoming events:",
            intent=intent,
            timetable=None,
            bus_routes=None,
            events=events,
            exams=None,
            faqs=None,
        )
    
    elif intent == "exam_schedule_query":
        result = await db.execute(select(models.ExamSchedule).limit(20))
        rows = list(result.scalars().all())
        exams = [
            schemas.ExamScheduleOut.model_validate(r, from_attributes=True)
            for r in rows
        ]
        return schemas.ChatResponse(
            answer="Here's the exam schedule:",
            intent=intent,
            timetable=None,
            bus_routes=None,
            events=None,
            exams=exams,
            faqs=None,
        )
    
    # For FAQ and general queries, use concise RAG
    answer = generate_answer(payload.message)
    
    # Only attach FAQs if it's an FAQ query
    faqs = None
    if intent == "faq_query":
        result = await db.execute(select(models.FAQ).limit(5))
        rows = list(result.scalars().all())
        faqs = [
            schemas.FAQOut.model_validate(r, from_attributes=True) for r in rows
        ]

    return schemas.ChatResponse(
        answer=answer,
        intent=intent,
        timetable=None,
        bus_routes=None,
        events=None,
        exams=None,
        faqs=faqs,
    )


