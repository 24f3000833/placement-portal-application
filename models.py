from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


#Admin table
class Admin(db.Model):
    __tablename__="admin"
    id=db.Column(db.Integer , primary_key=True)
    username=db.Column(db.String(50),unique=True,nullable = False )
    password=db.Column(db.String(250),nullable=False)

#Company table
class Company(db.Model):
    __tablename__="company"
    id=db.Column(db.Integer , primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(100), unique=True , nullable=False)
    password=db.Column(db.String(250),nullable=False)
    website=db.Column(db.String(100))
    certificate= db.Column(db.String(250) , nullable = False)
    approval_status=db.Column(db.String(20) , default="Pending")
    is_blacklisted= db.Column(db.Boolean , default=False)
    created_at=db.Column(db.DateTime , default=datetime.utcnow)
    
    drives=db.relationship("PlacementDrive",backref="company", lazy=True)

#Student table
class Student(db.Model):
    __tablename__="student"
    id=db.Column(db.Integer , primary_key=True)
    name=db.Column(db.String(100),nullable=False)
    email=db.Column(db.String(100), unique=True , nullable=False)
    password=db.Column(db.String(250),nullable=False)
    phone= db.Column(db.String(20))
    degree=db.Column(db.String(50), nullable=False )
    branch=db.Column(db.String(50), nullable=False)
    cgpa =db.Column(db.Float, nullable=False)
    resume=db.Column(db.String(200), nullable=False)
    is_blacklisted = db.Column(db.Boolean, default=False)
    created_at= db.Column(db.DateTime , default=datetime.utcnow)

    applications=db.relationship("Application",backref ="student", lazy=True)



#Placement Drive table
class PlacementDrive(db.Model):
    __tablename__="placement_drive"
    id=db.Column(db.Integer, primary_key=True)
    company_id=db.Column(db.Integer,db.ForeignKey("company.id"), nullable=False)
    job_title=db.Column(db.String(150), nullable=False)
    job_description=db.Column(db.Text)
    eligibility=db.Column(db.Text)
    salary= db.Column(db.String(50))
    location =db.Column(db.String(200))
    deadline = db.Column(db.Date)
    status= db.Column(db.String(25), default="Pending")
    created_at=db.Column(db.DateTime ,  default=datetime.utcnow)


    applications=db.relationship("Application" , backref="drive" , lazy =  True)

#Application Table
class Application(db.Model):
    __tablename__="application"
    id=db.Column(db.Integer , primary_key=True)
    student_id=db.Column(db.Integer, db.ForeignKey("student.id"), nullable= False)
    drive_id=db.Column(db.Integer, db.ForeignKey("placement_drive.id"), nullable=False)
    applied_at=db.Column(db.DateTime, default=datetime.utcnow)
    status=db.Column(db.String(25), default="Applied")

    __table_args__=(db.UniqueConstraint("student_id","drive_id",name="unique_application"), ) 

    



    

