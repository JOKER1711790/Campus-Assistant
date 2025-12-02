"""
Study-focused endpoints for the Smart Campus Assistant.

Features:
- Upload study materials (PDF/notes) per user
- Summarize a document
- Simple quiz generation from a document
- Simple Q&A over a single document (keyword-based)
"""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import List

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import auth, models, schemas
from app.db import get_db


router = APIRouter(prefix="/study", tags=["Study"])


UPLOAD_ROOT = Path("uploads")
UPLOAD_ROOT.mkdir(exist_ok=True)


async def get_current_user(
    current_user: models.User = Depends(auth.get_current_user),
) -> models.User:
    return current_user


def _extract_text_from_pdf(file_path: Path) -> str:
    try:
        from pypdf import PdfReader

        reader = PdfReader(str(file_path))
        texts: list[str] = []
        for page in reader.pages:
            page_text = page.extract_text() or ""
            texts.append(page_text)
        return "\n\n".join(texts).strip()
    except Exception as exc:  # pragma: no cover - best-effort extraction
        raise RuntimeError(f"Failed to extract text from PDF: {exc}") from exc


def _extract_text(file_path: Path, content_type: str | None) -> str:
    suffix = file_path.suffix.lower()

    if suffix == ".pdf" or (content_type and "pdf" in content_type):
        return _extract_text_from_pdf(file_path)

    # Fallback: treat as plain text
    try:
        return file_path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return file_path.read_text(encoding="latin-1")


@router.post(
    "/documents/upload",
    response_model=schemas.UserDocumentOut,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Upload a study document (PDF / text).

    - Saves the raw file under `uploads/<user_id>/`
    - Extracts text and stores it in the database
    """

    user_dir = UPLOAD_ROOT / f"user_{current_user.id}"
    user_dir.mkdir(parents=True, exist_ok=True)

    safe_name = os.path.basename(file.filename or "document")
    dest_path = user_dir / safe_name

    content = await file.read()
    dest_path.write_bytes(content)

    text = _extract_text(dest_path, file.content_type)
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not extract text from the uploaded document.",
        )

    doc = models.UserDocument(
        owner_id=current_user.id,
        title=safe_name,
        original_filename=safe_name,
        content_type=file.content_type,
        file_path=str(dest_path),
        text_content=text,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)

    return schemas.UserDocumentOut.model_validate(doc, from_attributes=True)


@router.get("/documents", response_model=List[schemas.UserDocumentOut])
async def list_documents(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """List documents uploaded by the current user."""

    result = await db.execute(
        select(models.UserDocument).where(
            models.UserDocument.owner_id == current_user.id
        )
    )
    docs = result.scalars().all()
    return [
        schemas.UserDocumentOut.model_validate(d, from_attributes=True) for d in docs
    ]


def _split_into_sentences(text: str) -> list[str]:
    # Simple sentence splitter based on punctuation
    parts = re.split(r"(?<=[.!?])\s+", text.strip())
    return [p.strip() for p in parts if p.strip()]


@router.post(
    "/documents/{document_id}/summarize", response_model=schemas.DocumentSummary
)
async def summarize_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Very simple extractive summarization:
    - Split into sentences
    - Take the first N sentences (or fewer if short)
    """

    doc = await db.get(models.UserDocument, document_id)
    if not doc or doc.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    sentences = _split_into_sentences(doc.text_content)
    if not sentences:
        summary = "No textual content could be extracted from this document."
    else:
        # Take first 5 sentences or up to 800 characters
        summary = " ".join(sentences[:5])
        if len(summary) > 800:
            summary = summary[:800] + "..."

    return schemas.DocumentSummary(document_id=document_id, summary=summary)


@router.post(
    "/documents/{document_id}/quiz",
    response_model=schemas.QuizResponse,
)
async def generate_quiz(
    document_id: int,
    num_questions: int = 5,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Extremely simple quiz generator:
    - Split text into sentences
    - Pick sentences with at least 6 words
    - For each, blank out a non-trivial word to form a question
    """

    import random

    doc = await db.get(models.UserDocument, document_id)
    if not doc or doc.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    sentences = _split_into_sentences(doc.text_content)
    candidates = [s for s in sentences if len(s.split()) >= 6]

    if not candidates:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Not enough content to generate a quiz.",
        )

    random.shuffle(candidates)
    questions: list[schemas.QuizQuestion] = []

    for sent in candidates[: num_questions * 2]:  # some extra to filter
        words = sent.split()
        # choose a word that is not too short
        content_word_indices = [
            i for i, w in enumerate(words) if len(re.sub(r"\\W", "", w)) >= 4
        ]
        if not content_word_indices:
            continue
        idx = random.choice(content_word_indices)
        answer = re.sub(r"\\W", "", words[idx])
        if not answer:
            continue
        words[idx] = "____"
        question_text = " ".join(words)

        # Generate simple distractors by modifying the answer
        distractors = {
            answer[::-1],
            answer.lower(),
            answer.upper(),
        }
        distractors = {d for d in distractors if d and d != answer}
        options = [answer] + list(distractors)
        random.shuffle(options)
        correct_index = options.index(answer)

        questions.append(
            schemas.QuizQuestion(
                question=question_text,
                options=options,
                correct_index=correct_index,
            )
        )

        if len(questions) >= num_questions:
            break

    if not questions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Could not generate quiz questions from this document.",
        )

    return schemas.QuizResponse(document_id=document_id, questions=questions)


@router.post("/documents/{document_id}/qa")
async def document_qa(
    document_id: int,
    question: str,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    """
    Very simple keyword-based Q&A over a single document:
    - Split the text into paragraphs
    - Score each paragraph by keyword overlap with the question
    - Return the best-matching paragraph as the answer
    """

    import math

    doc = await db.get(models.UserDocument, document_id)
    if not doc or doc.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")

    paragraphs = [p.strip() for p in doc.text_content.split("\n\n") if p.strip()]
    if not paragraphs:
        return {
            "answer": "I could not find any readable text in this document.",
            "document_id": document_id,
        }

    question_tokens = {
        t.lower()
        for t in re.findall(r"[A-Za-z0-9]+", question)
        if len(t) > 2
    }
    if not question_tokens:
        return {
            "answer": "Please ask a more specific question about the document.",
            "document_id": document_id,
        }

    best_score = -1.0
    best_para = paragraphs[0]

    for para in paragraphs:
        tokens = {
            t.lower()
            for t in re.findall(r"[A-Za-z0-9]+", para)
            if len(t) > 2
        }
        if not tokens:
            continue
        overlap = question_tokens & tokens
        score = len(overlap) / math.sqrt(len(tokens))
        if score > best_score:
            best_score = score
            best_para = para

    return {
        "answer": best_para,
        "document_id": document_id,
    }


