from flask import Flask,request
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import datetime
from sqlalchemy.exc import *
import re
from authentication import generatetoken , tokenvalidationmiddleware
from sqlalchemy import create_engine ,inspect
from sqlalchemy.schema import DDL
import os

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
def createdatabase():
    """ function for creating databse

        returns:
            database name
        
        raises:
            OperationalError:
                if credentials for connecting to mysql are wrong
    """

    database = os.getenv('DATABASE')

    engine = create_engine('mysql+mysqlconnector://root:root@localhost:3306/')

    # Connect to MySQL server
    connection = engine.connect()

    # SQL statement to create database if does not exist
    query = DDL(f"CREATE DATABASE if not exists {database}")

    connection.execute(query)
    # Close the connection
    connection.close()

    return database

database = createdatabase()

# get name of database from createdatabase() function to connect to database
assignment.config['SQLALCHEMY_DATABASE_URI'] = f'mysql://root:root@localhost/{database}'
assignment.config['SQLALCHEMY_TRACK_MODIFICATIONS']= False
db = SQLAlchemy(assignment)


# Third table for course and student
Course_Student = db.Table('course_student',
    db.Column('courseid', db.Integer, db.ForeignKey('course.id' ,ondelete = 'CASCADE')),
    db.Column('studentid', db.Integer, db.ForeignKey('student.id',ondelete = 'CASCADE')),
    db.PrimaryKeyConstraint('courseid','studentid')
)

# Third table for course and teacher
Course_Teacher = db.Table('course_teacher',
    db.Column('courseid', db.Integer, db.ForeignKey('course.id',ondelete = 'CASCADE')),
    db.Column('teacherid', db.Integer, db.ForeignKey('teacher.id',ondelete = 'CASCADE')),
    db.PrimaryKeyConstraint('courseid','teacherid')
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


@assignment.route('/addcourse',methods = ['POST'])    # add logical endpoints eg to add courses /add-course; to get all courses /courses
def addcourse():
    """Endpoint for adding a course to the course table.
    Method
    ------
        POST

    Paramter
    --------
        name:str
            required:true
            the name of course
        description:str
            required:true
            Short description of course
        instructor:
            required:true
            the name of instructor
        duration:
            required:true
            duration of course
        start_date:
            required:true
            start date of course

    Returns
    -------
        string:
            states if same course is already present
            or new course is added to table
    Raises
    ------
        Operational Error:
            if any of above attributes are missing 
    """
    # function to add a new course to table    # docstring must in """docstring""" stating what endpoint doing, args/parameter details, return values
    # request.get_json()
    try:
        data = request.get_json()
        if data['name'] == "":      # since we designing endpoints -> request.form[] won't work use request.get_json() we will test these by postman
            return "Name is empty"
        
        if data['description'] == "":   # see if can raise custom exception 
            return "description is empty"
        
        if data['instructor'] == "":
            return "instructor is empty"
        
        if data['duration'] == "":
            return "duration is empty"
        
        if data['start_date'] == "":
            return "start_date is empty"
        
        name = data['name']
        description = data['description']
        instructor = data['instructor']
        duration = data['duration']
        start_date = data['start_date']

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

        response = {"error":"Please fill all fields"}
        return response


@assignment.route('/addstudent',methods = ['POST'])
def addstudent():
    """Endpoint for adding a Student to the student table.
    Method
    ------
        POST

    Paramter
    --------
        name:str
            required:true
            the name of student
        email:str
            required:true
                email address of student
        feepaid:
            required:true
            student fee status:paid or not paid

    Returns
    -------
        string:
            states if student with email id is already registered
            or new student is added to table
    Raises
    ------
        Operational Error:
            if any of above attributes are missing 
    """
    try:
        data = request.get_json()
        if data['name']=="":
            return "name is empty"
        
        if data['email']=="":
            return "email is empty"
        
        if data['feepaid'] == "":
            return "feepaid is empty"
        
        name = data['name']
        email = data['email']
        feepaid = data['feepaid']

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
        response = {"error":"Please fill all fields"}
        return response

@assignment.route('/addteacher',methods = ['POST'])
def addteacher():
    """Endpoint for adding a Teacher to the teacher table.
    Method
    ------
        POST

    Paramter
    --------
        name:str
            required:true
            name of teacher
        email:str
            required:true
                email address of teacher
        password:
            required:true
            password for teacher

    Returns
    -------
        string:
            states if teacher with email id is already registered
            or new teacher is added to table
    Raises
    ------
        Operational Error:
            if any of above attributes are missing 
    """
    try:
        data = request.get_json()
        if data['name'] == "":
            return "name is empty"
        
        if data['email'] == "":
            return "email is empty"
        
        if data['password'] == "":
            return "password is empty"
        
        name = data['name']
        email = data['email']
        password = data['password']

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

        response = {"error":"Please fill all fields"}
        return response


@assignment.route('/enrollcourse',methods=['POST'])
def enrollcourse():
    """Endpoint for enrolling a student to course.
    record will be added to course_student table
    Method
    ------
        POST

    Paramter
    --------
        email:str
            required:true
                email address of student
        course name:
            required:true
            course name to which student will get enrolled

    Returns
    -------
        string:
            states if student is already enrolled to course
            or student got enrolled to course
    Raises
    ------
        Operational Error:
            if any of above values are missing
        Intigrity Error:
            if student is already registered to same course 
    """
    try:
        data = request.get_json()
        if data['email'] == "":
            return "email is empty"
        
        if data['course name'] == "":
            return "course name is empty"
        
        studentemail = data['email']
        coursename = data['course name']

        studentdata = Student.query.filter(Student.email == studentemail,\
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

        return "Student is seccessfully enrolled to course"
    except OperationalError:
        response = {"error":"Please fill all fields"}
        return response
    except IntegrityError:
        response = {"Message":"This Student is already enrolled to same course"}
        return response

@assignment.route('/assignteacher',methods=['POST'])
def assignteacher():
    """Endpoint for Assigning a teacher to course.
        record will be added to course_teacher table
    Method
    ------
        POST

    Paramter
    --------
        email:str
            required:true
                email address of teacher
        course name:
            required:true
            course name to which teacher will get assigned

    Returns
    -------
        string:
            states if teacher is already assigned to course
            or teacher got assigned to course
    Raises
    ------
        Operational Error:
            if any of parameters are missing
        Intigrity Error:
            if teacher is already assigned to same course 
    """
    try:
        data = request.get_json()
        if data['email'] == "":
            return "email is empty"
        
        if data['course name'] == "":
            return "course name is empty"
        
        teacheremail = data['email']
        coursename = data['course name']

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
    except OperationalError:
        response = {"error":"Please fill all fields"}
        return response
    except IntegrityError:
        response = {"Message":"This teacher is already assigned to same course"}
        return response
    
@assignment.route('/getcourses',methods = ['GET'])
def getcourses():
    """Endpoint for retriving all courses from course table
    Method
    ------
        GET

    Returns
    -------
        JSON:
            data of all available courses from course table
    Raises
    ------
        Operational Error:
            if there is database connection issue  
    """
    try:
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
    except OperationalError:
        response = {"error":"Please check database connection"}
        return response


@assignment.route('/getcourse/<id>',methods = ['GET'])
def getcourse(id):
    """Endpoint for retriving a single course by id from course table
    
    Method
    ------
        GET

    Paramter
    --------
        id:int
            id of course which we want to retrive

    Returns
    -------
        JSON:
            data of course of given id
        string:
            stating that no course with given id is present

    Raises
    ------
        Operational Error:
            if there is database connection issue
    """
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

@assignment.route('/updatecourse/<id>',methods = ['PUT'])
def updatecourse(id):
    """Endpoint for updating a course record by id in course table

    Method
    ------
        PUT

    Paramter
    --------
        id:int
            id of course that needs to be updated

    Returns
    -------
        string:
            states course is updated or 
            course not available with given id
    Raises
    ------
        Operational Error:
            if any of parameters are missing or
            database connection issue
    """

    try:
        data = request.get_json()
        if data['name'] == "":
            return "Name is empty"
        
        if data['description'] == "":
            return "description is empty"
        
        if data['instructor'] == "":
            return "instructor is empty"
        
        if data['duration'] == "":
            return "duration is empty"
        
        if data['start_date'] == "":
            return "start_date is empty"
        
        courseid = id
        name = data['name']
        description = data['description']
        instructor = data['instructor']
        duration = data['duration']
        start_date = data['start_date']


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
    

@assignment.route('/deletecourse/<id>',methods = ['DELETE'])
def deletecourse(id):
    """Endpoint for deleting course from course table

    Method
    ------
        DELETE

    Paramter
    --------
        id:int
            id of course to delete

    Returns
    -------
        string:
            states if course is deleted or 
            course not present with given id
    Raises
    ------
        Operational Error:
            in case of database connection issue
    """
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
        

@assignment.route('/getstudents/<id>',methods = ['GET'])
def getstudent(id):
    """Endpoint for retriving data of students who are 
        enrolled to specific course
    Method
    ------
        GET

    Paramter
    --------
        id:int
            id of course

    Returns
    -------
        JSON:
            data of students enrolled to specific course
    Raises
    ------
        Operational Error:
            if there is database connection issue
    """
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


@assignment.route('/getteachers/<id>',methods = ['GET'])
def getteachers(id):
    # 
    """Endpoint for retriving list of teachers 
        who are assigned to specific course 
    Method
    ------
        GET

    Paramter
    --------
        id:int
            id of course

    Returns
    -------
        JSON:
            data of teachers assigned to specific course
    Raises
    ------
        Operational Error:
            if there is database connection issue
    """
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
    """Endpoint for Allowing teacher to login

    Method
    ------
        POST

    Paramter
    --------
        email:str
            required:true
            email address of teacher
        password:str
            required:true
            password of teacher

    Returns
    -------
        string:
            Json web token if login successfull or 
            login failed message
    Raises
    ------
        Operational Error:
            if there is database connection issue
    """
    try:
        data = request.get_json()

        if data['email'] == "":
            return "email is empty"
            
        if data['password'] == "":
            return "password is empty"
        
        email = data['email']
        password = data['password']

        
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
