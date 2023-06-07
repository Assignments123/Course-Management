from flask import Flask,request
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import datetime
from sqlalchemy.exc import *
import re
from authentication import generatetoken , tokenvalidationmiddleware


# assignment.config['MYSQL_HOST'] = "localhost"
# assignment.config['MYSQL_USER'] = "root"
# assignment.config['MYSQL_PASSWORD'] = "root"
# assignment.config['MYSQL_DB'] = "course_management"

# print("hostname",os.getenv('HOST'))
# print("username",os.getenv('USERNAME'))
# print("PASSWORD",os.getenv('PASSWORD'))
# print("DATABASE",os.getenv('DATABASE'))

# assignment.config['MYSQL_HOST'] = os.getenv('HOST')
# assignment.config['MYSQL_USER'] = os.getenv('USERNAME')
# assignment.config['MYSQL_PASSWORD'] = os.getenv('PASSWORD')
# assignment.config['MYSQL_DB'] = os.getenv('DATABASE')

# mysql = MySQL(assignment)



assignment = Flask(__name__)
assignment.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/course_management'
assignment.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
db = SQLAlchemy(assignment)


# Third table for course and student
Course_Student = db.Table('course_student',
    db.Column('courseid', db.Integer, db.ForeignKey('course.id')),
    db.Column('studentid', db.Integer, db.ForeignKey('student.id'))
)

# Third table for course and teacher
Course_Teacher = db.Table('course_teacher',
    db.Column('courseid', db.Integer, db.ForeignKey('course.id')),
    db.Column('teacherid', db.Integer, db.ForeignKey('teacher.id'))
)

# Model Course
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True , autoincrement = True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    instructor = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.String(50), nullable=False)
    start_date = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    # for representation after retriving a record
    # def __repr__(self):
    #     return f'<course:{self.name}>'

# Model Student
class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True,autoincrement = True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    feepaid = db.Column(db.String(10), default=False)
    courses = db.relationship('Course',secondary = Course_Student, backref='students', lazy="dynamic")
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    # for representation after retriving a record
    # def __repr__(self):
    #     return f'<Student:{self.name}>'
    
# Model teacher
class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(50), nullable = False)
    courses = db.relationship('Course',secondary = Course_Teacher, backref='teachers', lazy="dynamic")
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
    deleted_at = db.Column(db.DateTime, nullable=True)

    # for representation after retriving a record
    # def __repr__(self):
    #     return f'<Teacher:{self.name}>'
   

with assignment.app_context():
    db.create_all()


@assignment.route('/')
@tokenvalidationmiddleware
def index():
    # index function where token validation middleware/decorator is applied
    token = request.headers.get("Authorization")

    print("token inside index" , token)

    return "Course Management Assignment"


@assignment.route('/courses',methods = ['POST'])
def addcourse():
    # function to add a new course to table
    try:
        if request.form['name'] == "":
            return "Name is empty"
        
        if request.form['description'] == "":
            return "description is empty"
        
        if request.form['instructor'] == "":
            return "instructor is empty"
        
        if request.form['duration'] == "":
            return "duration is empty"
        
        if request.form['start_date'] == "":
            return "start_date is empty"
        
        name = request.form['name']
        description = request.form['description']
        instructor = request.form['instructor']
        duration = request.form['duration']
        start_date = request.form['start_date']

        # check if course with same name is already present or not
        result = Course.query.filter(Course.name == name,\
                                     Course.deleted_at == None).first()

        # if course already exists then dont create new record
        if result:
            return "Course with this name is already present"
        
        record = Course(
            name = name,
            description = description,
            instructor = instructor,
            duration = duration,
            start_date = start_date
        )
        db.session.add(record)
        db.session.commit()
    
        return "Course is added succesfully!!"
    
    except OperationalError as e:

        response = "Exception is occured " + str(e)
        return response


@assignment.route('/student',methods = ['POST'])
def addstudent():
    # function to add a new record of student
    try:
        if request.form['name']=="":
            return "name is empty"
        
        if request.form['email']=="":
            return "email is empty"
        
        if request.form['feepaid'] == "":
            return "feepaid is empty"
        
        name = request.form['name']
        email = request.form['email']
        feepaid = request.form['feepaid']

        string = re.compile(r'([A-Za-z0-9]+[._-])*[A-Za-z0-9]+@[A-Za-z0-9]+(\.[A-Z|a-z]{2,})+')
        if not re.fullmatch(string,email):
            data = {
                "status":"error",
                "message":"Invalid email address"
            }
            return data

        # check if email is already registered or not
        result = Student.query.filter(Student.email == email ,\
                                      Student.deleted_at == None).first()

        # if already registered then dont create new record
        if result:
            return "Student with this email id is already present"
        
        record = Student(
            name = name,
            email = email,
            feepaid = feepaid,
        )

        db.session.add(record)
        db.session.commit()

        return "Student is registered succesfully!!"
    
    except OperationalError as e:
        response = "Exception is occured"+str(e)
        return response

@assignment.route('/teacher',methods = ['POST'])
def addteacher():
    # function for registering a new teacher
    try:
        if request.form['name'] == "":
            return "name is empty"
        
        if request.form['email'] == "":
            return "email is empty"
        
        if request.form['password'] == "":
            return "password is empty"
        
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        result = Teacher.query.filter(Teacher.email == email,\
                                      Teacher.deleted_at == None).first()

        if result:
            return "Teacher with this email id is already registered"
        
        teacher = Teacher(
            email = email,
            name =name,
            password = password
        )

        db.session.add(teacher)
        db.session.commit()

        return "Teacher is registered succesfully!!"

    except OperationalError as e:

        response = "Exception is occured"+str(e)
        return response


@assignment.route('/enrollcourse',methods=['POST'])
def enrollcourse():
    # function to enroll a course to student
    if request.form['email'] == "":
        return "email is empty"
    
    if request.form['course name'] == "":
        return "course name is empty"
    
    studentemail = request.form['email']
    coursename = request.form['course name']

    studentdata = Student.query.filter(Student.name == studentemail,\
                                       Student.deleted_at == None).first()
    
    if studentdata:
        studentid = studentdata.id

    coursedata = Course.query.filter(Course.name == coursename,\
                                     Course.deleted_at == None).first()

    if coursedata:
        courseid = coursedata.id

    print("id are:",courseid,studentid)
    
    query = Course_Student.insert().values(
        courseid = courseid,
        studentid=studentid
    )

    db.session.execute(query)
    db.session.commit()

    return "Student is seccessdully enrolled to course"

@assignment.route('/assignteacher',methods=['POST'])
def assignteacher():
    # function to assign a teacher to perticular course

    if request.form['email'] == "":
        return "email is empty"
    
    if request.form['course name'] == "":
        return "course name is empty"
    
    teacheremail = request.form['email']
    coursename = request.form['course name']

    teacher = Teacher.query.filter(Teacher.email == teacheremail,\
                                   Teacher.deleted_at == None).first()

    if teacher:
        teacherid = teacher.id
    else:
        return f"No teacher is registered with email {teacheremail}"

    course = Course.query.filter(Course.name == coursename,\
                                 Course.deleted_at == None).first()

    if course:
        courseid = course.id
    else:
        return f"No course with name {coursename} is available"

    query = Course_Teacher.insert().values(
        courseid = courseid,
        teacherid = teacherid
    )

    db.session.execute(query)
    db.session.commit()

    return "teacher is succesfully assigned to course"

@assignment.route('/courses',methods = ['GET'])
def getcourses():
    # function to retrive all courses

    records = Course.query.filter(Course.deleted_at == None).all()
    result = []
    for record in records:
        result.append({
                "name":record.name,
                "description":record.description,
                "instructor":record.instructor,
                "duration":record.duration,
                "start_date":record.start_date
            })
        
    return result




@assignment.route('/courses/<id>',methods = ['GET'])
def getcourse(id):
    # function to retrive a single course by id
    courseid = id
    
    # filter accepts multiple conditions where 
    # filter_by accepts only one argument or condition
    records = Course.query.filter(Course.id == courseid,\
                                  Course.deleted_at == None).all()

    # check if query returns empty list as there is no record with given id
    if not records:
        return "No Course with this id found"

    result = []

    for record in records:
        result.append({
            "name":record.name,
            "description":record.description,
            "instructor":record.instructor,
            "duration":record.duration,
            "start_date":record.start_date 
        })
    
    return result

@assignment.route('/courses/<id>',methods = ['PUT'])
def updatecourse(id):
    # function to update a course of given id passed as an argument

    try:
        if request.form['name'] == "":
            return "Name is empty"
        
        if request.form['description'] == "":
            return "description is empty"
        
        if request.form['instructor'] == "":
            return "instructor is empty"
        
        if request.form['duration'] == "":
            return "duration is empty"
        
        if request.form['start_date'] == "":
            return "start_date is empty"
        
        courseid = id
        name = request.form['name']
        description = request.form['description']
        instructor = request.form['instructor']
        duration = request.form['duration']
        start_date = request.form['start_date']


        record = Course.query.filter(Course.id == courseid,\
                                        Course.deleted_at == None).first()

        if record:
            record.name = name
            record.description = description
            record.instructor = instructor
            record.duration = duration
            record.start_date = start_date
            db.session.commit()
            return "record is updated successfully"
        else:
            return "record with this id not found"

    except OperationalError as e:
        response = "Exception is occured"+str(e)
        return response
    

@assignment.route('/courses/<id>',methods = ['DELETE'])
def deletecourse(id):
    # function to delete a perticular course
    try:
        courseid = id

        record = Course.query.filter(Course.id == courseid,\
                                     Course.deleted_at == None).first()
        if record:
            # db.session.delete(record)
            record.deleted_at = datetime.datetime.utcnow()
            db.session.commit()
            return "record is deleted succesfully"
        else:
            return "no record with this id found"

    except OperationalError as e:
        response = "Exception is occured"+str(e)
        return response
        
@assignment.route('/students/<id>',methods = ['GET'])
def getstudent(id):
    # function to retrive a list of students enrolled to a specific Course
    try:
        courseid = id


        # for joining both course and student tables
        # result = db.session.query(Course,Student).select_from(
        #     Course_Student).join(Course).join(Student).filter(
        #     Course_Student.c.courseid == cid).all()
        
        # students = []
        # for course , student in result:
        #     students.append(student.name)
        # print(students)

        # for joining just studentdata as we need only student names 
        result = db.session.query(Student).select_from(
            Course_Student).join(Student).filter(
            Course_Student.c.courseid == courseid).all()
        
        if result:

            students = []
            for student in result:
                data = {
                    "name" : student.name,
                    "email" : student.email,
                }
                students.append(data)
            return students
        else:
            return "No record with this course id found"
    except OperationalError as e:
        response = {"error":"Exception is occured"+str(e)}
        return response


@assignment.route('/teachers/<id>',methods = ['GET'])
def getteachers(id):
    # function to retrive list of teachers who are assigned to a single course
    try:

        courseid = id

        result = db.session.query(Teacher).select_from(
                Course_Teacher).join(Teacher).filter(
                Course_Teacher.c.courseid == courseid).all()
        
        if result:
            teachers = []
            for teacher in result:
                data = {
                    "name":teacher.name,
                    "email":teacher.email
                }
                teachers.append(data)
                
            return teachers
        else:
            return "No record with this course id found"
    except OperationalError as e:
        response = {"error":"Exception is occured"+str(e)}
        return response


@assignment.route('/login',methods = ['POST'])
def login():
    # function to login a teacher
    try:
        if request.form['email'] == "":
            return "email is empty"
            
        if request.form['password'] == "":
            return "password is empty"
        
        email = request.form['email']
        password = request.form['password']

        result = Teacher.query.filter(Teacher.email == email).first()

        if not result:
            return "invalid credentials!!"

        if result.password == password:

            print("Correct credentials")

            token = generatetoken()

            return token
        
        else:
            return "login falied"     
    except Exception as e:
        response = {"error":"Exception is occured " + type(e).__name__ + " "+str(e)}
        return response


if __name__ == "__main__":
    assignment.run(debug=True)
