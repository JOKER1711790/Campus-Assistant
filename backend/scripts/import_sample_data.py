"""
Import sample CSV datasets from `datasets/` into the database.

Run from the `backend` directory (with venv activated):

    python -m scripts.import_sample_data
"""

import asyncio
import csv
from datetime import date, time
from pathlib import Path

from sqlalchemy import select

from app.db import AsyncSessionLocal
from app.models import (
    BusRoute,
    CampusEvent,
    Department,
    ExamSchedule,
    FAQ,
    FacultyMember,
    TimetableEntry,
)


ROOT = Path(__file__).resolve().parents[2]
DATASETS_DIR = ROOT / "datasets"


def parse_time(value: str) -> time:
    return time.fromisoformat(value)


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


async def import_faculty(session):
    path = DATASETS_DIR / "faculty.csv"
    if not path.exists():
        return

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dept = None
            if row.get("department_code"):
                existing = await session.execute(
                    select(Department).where(
                        Department.code == row["department_code"]
                    )
                )
                dept = existing.scalar_one_or_none()
                if dept is None:
                    dept = Department(
                        name=row["department_name"],
                        code=row["department_code"],
                    )
                    session.add(dept)
                    await session.flush()

            faculty = FacultyMember(
                name=row["name"],
                email=row.get("email") or None,
                phone=row.get("phone") or None,
                room=row.get("room") or None,
                designation=row.get("designation") or None,
                department_id=dept.id if dept else None,
            )
            session.add(faculty)


async def import_timetable(session):
    path = DATASETS_DIR / "timetable.csv"
    if not path.exists():
        return

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entry = TimetableEntry(
                program=row["program"],
                semester=int(row["semester"]),
                section=row["section"],
                day_of_week=row["day_of_week"],
                start_time=parse_time(row["start_time"]),
                end_time=parse_time(row["end_time"]),
                course_code=row["course_code"],
                course_title=row["course_title"],
                room=row.get("room") or None,
                faculty_name=row.get("faculty_name") or None,
            )
            session.add(entry)


async def import_bus_routes(session):
    path = DATASETS_DIR / "bus_routes.csv"
    if not path.exists():
        return

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            route = BusRoute(
                route_name=row["route_name"],
                origin=row["origin"],
                destination=row["destination"],
                departure_time=parse_time(row["departure_time"]),
                arrival_time=parse_time(row["arrival_time"]),
                days_of_week=row["days_of_week"],
            )
            session.add(route)


async def import_events(session):
    path = DATASETS_DIR / "events.csv"
    if not path.exists():
        return

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            event = CampusEvent(
                title=row["title"],
                description=row.get("description") or None,
                location=row.get("location") or None,
                start_date=parse_date(row["start_date"]),
                end_date=parse_date(row["end_date"]),
                is_all_day=row["is_all_day"].lower() == "true",
            )
            session.add(event)


async def import_exam_schedule(session):
    path = DATASETS_DIR / "exam_schedule.csv"
    if not path.exists():
        return

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            exam = ExamSchedule(
                program=row["program"],
                semester=int(row["semester"]),
                course_code=row["course_code"],
                course_title=row["course_title"],
                exam_date=parse_date(row["exam_date"]),
                start_time=parse_time(row["start_time"]),
                end_time=parse_time(row["end_time"]),
                room=row.get("room") or None,
            )
            session.add(exam)


async def import_faqs(session):
    path = DATASETS_DIR / "faqs.csv"
    if not path.exists():
        return

    with path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            faq = FAQ(
                question=row["question"],
                answer=row["answer"],
                category=row.get("category") or None,
            )
            session.add(faq)


async def main():
    async with AsyncSessionLocal() as session:
        await import_faculty(session)
        await import_timetable(session)
        await import_bus_routes(session)
        await import_events(session)
        await import_exam_schedule(session)
        await import_faqs(session)
        await session.commit()
    print("Sample data imported successfully.")


if __name__ == "__main__":
    asyncio.run(main())



