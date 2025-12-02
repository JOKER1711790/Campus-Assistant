# Datasets Directory

Place your real campus data CSV files here.

## Required Files (Optional - only include what you have)

- `timetable.csv` - Class schedules
- `bus_routes.csv` - Bus/shuttle schedules  
- `events.csv` - Campus events and announcements
- `exam_schedule.csv` - Exam timetables
- `faculty.csv` - Faculty directory
- `faqs.csv` - Frequently asked questions

## Format Requirements

See `DATA_PREPARATION_GUIDE.md` for detailed CSV format specifications.

## Quick Start

1. Prepare your CSV files with the correct column headers
2. Place them in this directory
3. Run: `cd backend && python -m scripts.import_sample_data`
4. Build RAG index: `cd backend && python -m scripts.build_sample_rag_index`

## For PDFs and Text Documents

Create a subdirectory `notices/` and place your PDF/text files there, then use:
`backend/scripts/build_real_rag_index.py` to index them.

