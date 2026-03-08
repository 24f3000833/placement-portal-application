from flask import Flask , render_template , request, redirect,url_for,session , flash , Response
from models import db , Admin , Company , Student , PlacementDrive, Application
from werkzeug.security import generate_password_hash , check_password_hash
from werkzeug.utils import secure_filename
import os


app= Flask(__name__)
app.config["SECRET_KEY"]="placementportaljan26"  #USed to encrypt session data and keeps login into safe
app.config["SQLALCHEMY_DATABASE_URI"]= "sqlite:///placement.db"  #CReate placement.db file and store all 5 tables 
app.config["SQLALCHEMY_TRACK_MODIFICATION"]=False  #Removes unneccessary features and saves memory anbd time
app.config["UPLOAD_FOLDER"]="static/upload"  #Stores the uploaded file (certificate and resumnes)
app.config["MAX_CONTENT_LENGTH"]=16*1024*1024   #Max file upload size = 16MB


db.init_app(app)


#Home Route
@app.route("/")
def home():
    return render_template("home.html")



#LOGIN Route
@app.route("/login", methods=["GET","POST"])
def login():
    if "user_id" in session:
        if session["role"]=="student":
            return redirect(url_for("student_dashboard"))
        elif session["role"]=="company":
            return redirect(url_for("company_dashboard"))
    if request.method=="POST":
        email= request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")

      
        
        if role=="company":
            company=Company.query.filter_by(email=email).first()
            if company and check_password_hash(company.password , password):
                if company.is_blacklisted:
                    flash("Your account is blacklisted","danger")
                    return redirect(url_for("login"))
                if company.approval_status=="Pending":
                    flash("Your approval is pending..Wait some time!!", "warning")
                    return redirect(url_for("login"))
                if company.approval_status=="Rejected":
                    flash("Your approval is rejected", "danger")
                    return redirect(url_for("login"))
                session["user_id"]=company.id
                session["role"]="company"
                flash("Welcome "+company.name, "success")
                return redirect(url_for("company_dashboard"))
            else:
                flash("Invalid company credentials","danger")
                return redirect(url_for("login"))
        

        elif role=="student":
            student=Student.query.filter_by(email=email).first()
            if student and check_password_hash(student.password,password):
                if student.is_blacklisted:
                    flash("Your account is blacklisted","danger")
                    return redirect(url_for("login"))
                session["user_id"]=student.id
                session["role"]= 'student'
                flash("Welcome "+student.name,"success")
                return redirect(url_for("student_dashboard"))
            else:
                flash("Invalid student credentials", "danger")
                return redirect(url_for("login"))
    
    return render_template("auth/login.html")
                

@app.route('/admin/login', methods=["GET" , "POST"])
def admin_login():
    if "user_id" in session:
        if session["role"]=="admin":
            return redirect(url_for("admin_dashboard"))
    if request.method=="POST":
        username=request.form.get("username", "")
        password=request.form.get("password","")
        admin=Admin.query.filter_by(username=username).first()
        if admin and check_password_hash(admin.password, password):
            session["user_id"]=admin.id
            session["role"]="admin"
            flash("Welcome Admin!", "success")
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid admin credentials!","danger")
            return redirect(url_for("login"))
    return render_template("auth/admin_login.html")





@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully","success")
    return redirect(url_for("login"))


@app.route("/register/student" , methods=["GET", "POST"])
def register_student():
    if request.method=="POST":
        name=request.form.get("name","")
        email=request.form.get("email","")
        password=request.form.get("password","")
        phone=request.form.get("phone","")
        degree=request.form.get("degree","")
        branch=request.form.get("branch","")
        cgpa=request.form.get("cgpa","")
        resume=request.files.get("resume")

        existing=Student.query.filter_by(email=email).first()
        if existing:
            flash("Email alrerady registered","danger")
            return redirect(url_for("register_student"))
        
        if resume:
            filename=secure_filename(resume.filename)
            resume_folder=os.path.join(app.config["UPLOAD_FOLDER"],"resumes")
            os.makedirs(resume_folder , exist_ok=True)
            resume.save(os.path.join(resume_folder, filename))
        else:
            flash("Please upload your resume","danger")
            return redirect(url_for("register_student"))
        
        hashed_password=generate_password_hash(password)
        student=Student(
            name=name,
            email=email,
            password=hashed_password,
            phone=phone,
            degree=degree,
            branch=branch,
            cgpa=float(cgpa),
            resume=filename
        )
        db.session.add(student)
        db.session.commit()

        flash("Registration Successful..Please login to continue","success")
        return redirect(url_for("login"))
    return render_template("auth/register_student.html")




@app.route("/register/company" , methods=["GET", "POST"])
def register_company():
    if request.method=="POST":
        name=request.form.get("name","")
        email=request.form.get("email","")
        password=request.form.get("password","")
        website=request.form.get("website","")
        certificate=request.files.get("certificate")

        existing=Company.query.filter_by(email=email).first()
        if existing:
            flash("Email alrerady registered","danger")
            return redirect(url_for("register_company"))
        
        if certificate:
            filename=secure_filename(certificate.filename)
            certificate_folder=os.path.join(app.config["UPLOAD_FOLDER"],"certificates")
            os.makedirs(certificate_folder , exist_ok=True)
            certificate.save(os.path.join(certificate_folder, filename))
        else:
            flash("Please upload your Certificate","danger")
            return redirect(url_for("register_company"))
        
        hashed_password=generate_password_hash(password)
        company=Company(
            name=name,
            email=email,
            password=hashed_password,
            website=website,
            certificate=filename,
            approval_status="Pending"
        )
            
        
        db.session.add(company)
        db.session.commit()

        flash("Registration Successful...Wait for admin approval","warning")
        return redirect(url_for("login"))
    return render_template("auth/register_company.html")





@app.route("/admin/dashboard")
def admin_dashboard():
    return "Admin Dashboard--COming soon..."


@app.route("/company/dashboard")
def company_dashboard():
    return "Company Dashboard--COming soon..."


@app.route("/student/dashboard")
def student_dashboard():
    return "Student--COming soon..."



if __name__=="__main__":
    app.run(debug=True)

                
