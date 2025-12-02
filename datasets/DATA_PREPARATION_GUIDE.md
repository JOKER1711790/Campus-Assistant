# Real Data Implementation Guide

This guide shows you how to prepare and import your real campus data.

## Step 1: Prepare Your CSV Files

Place your CSV files in the `datasets/` directory. Each CSV must have the exact column headers shown below.

### 1. Timetable (`timetable.csv`)

**Required columns:**
- `program` - e.g., "B.Tech CSE", "M.Tech IT"
- `semester` - integer (1, 2, 3, etc.)
- `section` - e.g., "A", "B", "C"
- `day_of_week` - uppercase 3-letter code: "MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"
- `start_time` - format: "HH:MM" or "HH:MM:SS" (e.g., "09:00" or "09:00:00")
- `end_time` - format: "HH:MM" or "HH:MM:SS"
- `course_code` - e.g., "CS201", "MATH101"
- `course_title` - full course name
- `room` - optional, e.g., "CS-101"
- `faculty_name` - optional, e.g., "Dr. A. Sharma"

**Example:**
```csv
program,semester,section,day_of_week,start_time,end_time,course_code,course_title,room,faculty_name
B.Tech CSE,3,A,MON,09:00,10:00,CS201,Data Structures,CS-101,Dr. A. Sharma
B.Tech CSE,3,A,TUE,10:00,11:00,CS203,Algorithms,CS-102,Dr. R. Verma
```

---

### 2. Bus Routes (`bus_routes.csv`)

**Required columns:**
- `route_name` - e.g., "Route 1", "Main Campus Shuttle"
- `origin` - starting location
- `destination` - ending location
- `departure_time` - format: "HH:MM" or "HH:MM:SS"
- `arrival_time` - format: "HH:MM" or "HH:MM:SS"
- `days_of_week` - e.g., "MON-FRI", "SAT", "SUN", "MON,WED,FRI"

**Example:**
```csv
route_name,origin,destination,departure_time,arrival_time,days_of_week
Route 1,Main Gate,Engineering Block,08:00,08:30,MON-FRI
Route 2,Hostel,Library,09:00,09:15,MON-FRI
```

---

### 3. Events (`events.csv`)

**Required columns:**
- `title` - event name
- `description` - optional, event details
- `location` - optional, venue
- `start_date` - format: "YYYY-MM-DD" (e.g., "2025-03-15")
- `end_date` - format: "YYYY-MM-DD" (can be same as start_date for single-day events)
- `is_all_day` - "true" or "false" (lowercase)

**Example:**
```csv
title,description,location,start_date,end_date,is_all_day
Tech Fest 2025,Annual technical festival with workshops,Auditorium,2025-04-10,2025-04-12,false
Orientation Session,Welcome session for new students,Main Hall,2025-03-01,2025-03-01,true
```

---

### 4. Exam Schedule (`exam_schedule.csv`)

**Required columns:**
- `program` - e.g., "B.Tech CSE"
- `semester` - integer
- `course_code` - e.g., "CS201"
- `course_title` - full course name
- `exam_date` - format: "YYYY-MM-DD"
- `start_time` - format: "HH:MM" or "HH:MM:SS"
- `end_time` - format: "HH:MM" or "HH:MM:SS"
- `room` - optional, exam hall/room

**Example:**
```csv
program,semester,course_code,course_title,exam_date,start_time,end_time,room
B.Tech CSE,3,CS201,Data Structures,2025-05-15,09:00,12:00,Exam Hall A
B.Tech CSE,3,CS203,Algorithms,2025-05-17,14:00,17:00,Exam Hall B
```

---

### 5. Faculty Directory (`faculty.csv`)

**Required columns:**
- `name` - full name
- `email` - optional
- `phone` - optional
- `room` - optional, office room number
- `designation` - optional, e.g., "Professor", "Associate Professor"
- `department_code` - optional, e.g., "CSE", "ECE"
- `department_name` - optional, e.g., "Computer Science Engineering"

**Example:**
```csv
name,email,phone,room,designation,department_code,department_name
Dr. A. Sharma,asharma@university.edu,1234567890,CS-201,Professor,CSE,Computer Science Engineering
Dr. R. Verma,rverma@university.edu,0987654321,CS-202,Associate Professor,CSE,Computer Science Engineering
```

---

### 6. FAQs (`faqs.csv`)

**Required columns:**
- `question` - the question text
- `answer` - the answer text
- `category` - optional, e.g., "General", "Academic", "Administrative"

**Example:**
```csv
question,answer,category
Where can I see my timetable?,You can view your timetable on the student portal under Academics section.,Academic
How can I get my ID card?,Collect your ID card from the administrative office between 10 AM and 4 PM on working days.,Administrative
Is there Wi-Fi on campus?,Yes, Wi-Fi is available throughout the campus. Connect to "CampusWiFi" network.,General
```

---

## Step 2: Import Your Data

Once your CSV files are ready in the `datasets/` directory:

```bash
cd backend
python -m scripts.import_sample_data
```

This will:
- Read all CSV files from `datasets/`
- Import them into the database
- Create departments automatically if needed (for faculty)

**Note:** The script will skip files that don't exist, so you can import only the data you have.

---

## Step 3: Build RAG Index for Documents

For PDFs, notices, and other text documents:

### Option A: Add to FAQs/Events CSV (Simple)

If you have short notices or announcements, add them to:
- `faqs.csv` (for Q&A format)
- `events.csv` (for event descriptions)

The RAG index will automatically include these when you run the build script.

### Option B: Create a Custom RAG Index Script (For PDFs/Long Documents)

1. **Extract text from PDFs:**
   ```python
   # Example: extract_text_from_pdf.py
   from pypdf import PdfReader
   
   reader = PdfReader("notice.pdf")
   text = ""
   for page in reader.pages:
       text += page.extract_text()
   ```

2. **Create a script to build RAG index:**
   ```python
   # backend/scripts/build_real_rag_index.py
   from pathlib import Path
   from app.rag import RAGEngine
   
   documents = [
       ("Your extracted text here", "source_notice_1"),
       ("Another document text", "source_notice_2"),
   ]
   
   engine = RAGEngine()
   engine.build_index(documents)
   print("RAG index built successfully!")
   ```

3. **Run it:**
   ```bash
   cd backend
   python -m scripts.build_real_rag_index
   ```

---

## Step 4: Verify Your Data

1. **Check the database:**
   - Open `http://localhost:8000/docs`
   - Test endpoints like `/api/timetable`, `/api/events`, etc.

2. **Test the chatbot:**
   - Ask questions relevant to your data
   - Verify responses are accurate

---

## Tips for Data Preparation

1. **Time formats:** Always use 24-hour format (09:00, not 9:00 AM)
2. **Dates:** Use ISO format (YYYY-MM-DD)
3. **Day codes:** Use uppercase 3-letter codes (MON, TUE, not Monday, Tuesday)
4. **Encoding:** Save CSVs as UTF-8 to handle special characters
5. **Empty fields:** Leave empty or use empty string (not "NULL" or "N/A")

---

## Troubleshooting

**Import fails:**
- Check CSV column headers match exactly (case-sensitive)
- Verify date/time formats are correct
- Check for special characters that might break parsing

**RAG not working:**
- Make sure you ran `build_sample_rag_index.py` or your custom RAG script
- Check that `.cache/embeddings/` directory exists with `index.faiss` file

**Data not showing:**
- Verify data was imported (check database file `smart_campus.db`)
- Restart the backend server
- Check API responses in Swagger docs

