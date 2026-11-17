from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field
from fastapi.responses import RedirectResponse
import sqlite3

class Student(BaseModel):
    name: str
    age: int = Field(ge=18, le=30)
    gender: str
    marks: int
    course: str
    image: str
    status: int = Field(ge=0, le=1)

def get_connection():
    connection = sqlite3.connect("students.db")
    return connection

def create_table():
    connection = get_connection()
    cursor = connection.cursor()

    q = """
    CREATE TABLE IF NOT EXISTS students(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        age INTEGER,
        gender TEXT,
        marks INTEGER,
        course TEXT,
        image TEXT,
        status INTEGER
    )
    """

    cursor.execute(q)
    connection.commit()
    connection.close()

create_table()

templates = Jinja2Templates(directory="templates")

app = FastAPI()

@app.get("/")
def home(req: Request):
    connection = get_connection()
    cursor = connection.cursor()

    q = "SELECT * FROM students"
    cursor.execute(q)
    students = cursor.fetchall()

    connection.close()

    return templates.TemplateResponse(
        request=req,
        name="home.html",
        context={"stds": students}
    )

@app.get("/students/add")
def send_std_form(req: Request):
    return templates.TemplateResponse(
        request=req,
        name="add-student.html",
        context={}
    )

@app.post("/students/add")
def create_std(
    name: str = Form(),
    age: int = Form(),
    gender: str = Form(),
    marks: int = Form(),
    course: str = Form(),
    image: str = Form(),
    status: int = Form()
):
    students = Student(
        name=name,
        age=age,
        gender=gender,
        marks=marks,
        course=course,
        image=image,
        status=status
    )

    values = (
        students.name,
        students.age,
        students.gender,
        students.marks,
        students.course,
        students.image,
        students.status
    )

    connection = get_connection()
    cursor = connection.cursor()

    q = """
    INSERT INTO students(name, age, gender, marks, course, image, status)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """

    cursor.execute(q, values)
    connection.commit()
    connection.close()

    return RedirectResponse(url="/", status_code=303)

@app.post("/std/delete/{std_id}")
def delete_std(std_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    q = "DELETE FROM students WHERE id=?"
    cursor.execute(q, (std_id,))

    connection.commit()
    connection.close()

    return RedirectResponse(url="/", status_code=303)

@app.get("/students/{std_id}")
def single_std(req: Request, std_id: int):
    connection = get_connection()
    cursor = connection.cursor()

    q = "SELECT * FROM students WHERE id=?"
    cursor.execute(q, (std_id,))
    student = cursor.fetchone()

    connection.close()

    return templates.TemplateResponse(
        request=req,
        name="single-std.html",
        context={"std": student}
    )


@app.get("/students/edit/{std_id}")
def edit_std(req: Request, std_id: int):

    connection = get_connection()
    cursor = connection.cursor()

    q = "SELECT * FROM students WHERE id=?"
    cursor.execute(q, (std_id,))
    student = cursor.fetchone()

    connection.close()

    return templates.TemplateResponse(
        request=req,
        name="edit-student.html",
        context={"std": student}
    )

@app.post("/students/edit/{std_id}")
def update_std(
    std_id: int,
    name: str = Form(),
    age: int = Form(),
    gender: str = Form(),
    marks: int = Form(),
    course: str = Form(),
    image: str = Form(),
    status: int = Form()
):

    students = Student(
        name=name,
        age=age,
        gender=gender,
        marks=marks,
        course=course,
        image=image,
        status=status
    )

    connection = get_connection()
    cursor = connection.cursor()

    q = """
    UPDATE students
    SET name=?, age=?, gender=?, marks=?, course=?, image=?, status=?
    WHERE id=?
    """

    values = (
        students.name,
        students.age,
        students.gender,
        students.marks,
        students.course,
        students.image,
        students.status,
        std_id
    )

    cursor.execute(q, values)
    connection.commit()
    connection.close()

    return RedirectResponse(url="/", status_code=303)
