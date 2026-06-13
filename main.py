from fastapi import FastAPI
from pydantic import BaseModel
from database import SessionLocal, Thread, Message
from dotenv import load_dotenv
from groq import Groq
import os

load_dotenv()

app = FastAPI()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


class ChatRequest(BaseModel):
    thread_id: int
    message: str


@app.post("/threads")
def create_thread():

    db = SessionLocal()

    try:
        thread = Thread(
            title="New Chat"
        )

        db.add(thread)
        db.commit()
        db.refresh(thread)

        return {
            "id": thread.id
        }

    finally:
        db.close()


@app.get("/threads")
def get_threads():

    db = SessionLocal()

    try:
        threads = db.query(Thread).all()

        return [
            {
                "id": t.id,
                "title": t.title
            }
            for t in threads
        ]

    finally:
        db.close()


@app.get("/threads/{thread_id}")
def get_messages(thread_id: int):

    db = SessionLocal()

    try:
        messages = (
            db.query(Message)
            .filter(Message.thread_id == thread_id)
            .all()
        )

        return [
            {
                "role": m.role,
                "content": m.content
            }
            for m in messages
        ]

    finally:
        db.close()


@app.post("/chat")
def chat(req: ChatRequest):

    db = SessionLocal()

    try:
        user_msg = Message(
            thread_id=req.thread_id,
            role="user",
            content=req.message
        )

        db.add(user_msg)
        db.commit()

        thread = db.query(Thread).filter(
            Thread.id == req.thread_id
        ).first()

        if thread and thread.title == "New Chat":
            thread.title = req.message[:25]
            db.commit()

        all_messages = db.query(Message).all()

        llm_messages = []

        for msg in all_messages:
            llm_messages.append(
                {
                    "role": msg.role,
                    "content": msg.content
                }
            )

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=llm_messages
        )

        answer = response.choices[0].message.content

        assistant_msg = Message(
            thread_id=req.thread_id,
            role="assistant",
            content=answer
        )

        db.add(assistant_msg)
        db.commit()

        return {
            "response": answer
        }

    finally:
        db.close()