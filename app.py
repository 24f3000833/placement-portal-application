from flask import Flask , render_template , request, redirect,url_for,session , flash , Response , send_from_directory
from models import db , Admin , Company , Student , PlacementDrive, Application
from werkzeug.security import generate_password_hash , check_password_hash
from werkzeug.utils import secure_filename
import os
from datetime import datetime , date


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
    return redirect(url_for("login"))


############  AUTHENTICATION WORKSS  ###############################
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
                
#Admin Login
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

#Student registration
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



#Company registration
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

####################################################################


####  ADMIN AND ITS FUNCTIONS  ######

#Admin dashboard
@app.route("/admin/dashboard")
def admin_dashboard():
    if "user_id" not in session or session["role"] != "admin":
        flash("Please login as Admin","danger")
        return redirect(url_for("admin_login"))
    
    search = request.args.get("search", "").strip()

    
    total_students=Student.query.count()
    total_companies=Company.query.count()
    total_drives=PlacementDrive.query.count()
    total_applications=Application.query.count()

    pending_companies=Company.query.filter_by(approval_status="Pending").all()
    all_companies=Company.query.filter_by(approval_status="Approved").all()
    all_students=Student.query.all()
    ongoing_drives=PlacementDrive.query.filter_by(status="Approved").all()
    all_applications = Application.query.order_by(Application.applied_at.desc()).limit(20).all()
    pending_drives = PlacementDrive.query.filter_by(status="Pending").all()
    all_drives = PlacementDrive.query.order_by(PlacementDrive.created_at.desc()).all()


    if search:
        
        is_digit = search.isdigit()

        
        pending_companies = Company.query.filter(
            Company.approval_status == "Pending",
            (Company.name.ilike(f"%{search}%")) |
            (Company.id == int(search) if is_digit else False)
        ).all()

        
        all_companies = Company.query.filter(
            Company.approval_status == "Approved",
            (Company.name.ilike(f"%{search}%")) |
            (Company.id == int(search) if is_digit else False)
        ).all()


        all_students = Student.query.filter(
            (Student.name.ilike(f"%{search}%")) |
            (Student.id == int(search) if is_digit else False)
        ).all()

    else:
        
        pending_companies = Company.query.filter_by(approval_status="Pending").all()
        all_companies = Company.query.filter_by(approval_status="Approved").all()
        all_students = Student.query.all()

    return render_template("admin/admin_dashboard.html",
        total_students=total_students,
        total_companies=total_companies,
        total_drives=total_drives,
        total_applications=total_applications,
        pending_companies=pending_companies,
        all_companies=all_companies,
        all_students=all_students,
        ongoing_drives=ongoing_drives,
        search=search,
        all_applications=all_applications ,
        all_drives=all_drives , 
        pending_drives=pending_drives
    )

@app.route("/admin/company/<int:id>/approve")
def approve_company(id):
    if "user_id" not in session or session["role"] != "admin":
        return redirect(url_for("admin_login"))
    company = Company.query.get_or_404(id)
    company.approval_status = "Approved"
    db.session.commit()
    flash(f"{company.name} has been approved!", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/company/<int:id>/reject")
def reject_company(id):
    if "user_id" not in session or session["role"] != "admin":
        return redirect(url_for("admin_login"))
    company = Company.query.get_or_404(id)
    name=company.name
    db.session.delete(company)
    db.session.commit()
    flash(f"{company.name} has been rejected", "warning")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/company/<int:id>/blacklist")
def blacklist_company(id):
    if "user_id" not in session or session["role"] != "admin":
        return redirect(url_for("admin_login"))
    company = Company.query.get_or_404(id)
    company.is_blacklisted = not company.is_blacklisted
    if company.is_blacklisted:
        for drive in company.drives:
            drive.status = "Closed"
        flash(f"{company.name} blacklisted...All drives closed", "danger")
    else:
        flash(f"{company.name} un-blacklisted", "success")
    db.session.commit()
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/student/<int:id>/blacklist")
def blacklist_student(id):
    if "user_id" not in session or session["role"] != "admin":
        return redirect(url_for("admin_login"))
    student = Student.query.get_or_404(id)
    student.is_blacklisted = not student.is_blacklisted
    action = "blacklisted" if student.is_blacklisted else "un-blacklisted"
    flash(f"{student.name} has been {action}", "warning")
    db.session.commit()
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/student/<int:id>/delete")
def delete_student(id):
    if "user_id" not in session or session["role"] != "admin":
        return redirect(url_for("admin_login"))
    student = Student.query.get_or_404(id)
    Application.query.filter_by(student_id=id).delete()
    db.session.delete(student)
    db.session.commit()
    flash("Student deleted successfully.", "success")
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/drive/<int:id>/approve")
def approve_drive(id):
    if "user_id" not in session or session["role"] != "admin":
        return redirect(url_for("admin_login"))
    drive = PlacementDrive.query.get_or_404(id)
    drive.status = "Approved"
    db.session.commit()
    flash(f"{drive.job_title} has been approved!", "success")
    return redirect(url_for("admin_drive_detail", id=id))

@app.route("/admin/drive/<int:id>/reject")
def reject_drive(id):
    if "user_id" not in session or session["role"] != "admin":
        return redirect(url_for("admin_login"))
    drive = PlacementDrive.query.get_or_404(id)
    drive.status = "Rejected"
    db.session.commit()
    flash(f"{drive.job_title} has been rejected.", "warning")
    return redirect(url_for("admin_drive_detail", id=id))

@app.route("/admin/drive/<int:id>/close")
def close_drive(id):
    if "user_id" not in session or session["role"] != "admin":
        return redirect(url_for("admin_login"))
    drive = PlacementDrive.query.get_or_404(id)
    drive.status = "Closed"
    db.session.commit()
    flash(f"{drive.job_title} has been closed.", "info")
    return redirect(url_for("admin_drive_detail", id=id))


@app.route("/admin/student/<int:id>")
def admin_student_detail(id):
    if "user_id" not in session or session["role"]!="admin":
        flash("Please login as Admin","danger")
        return redirect(url_for("admin_login"))
    student=Student.query.get_or_404(id)
    applications=Application.query.filter_by(student_id=id).all()
    joined_date=student.created_at.strftime("%d %b %Y")

    return render_template("admin/student_detail.html",student=student,applications=applications,joined_date=joined_date)

    

@app.route("/admin/company/<int:id>")
def admin_company_detail(id):
    if "user_id" not in session or session["role"] != "admin":
        flash("Please login as Admin", "danger")
        return redirect(url_for("admin_login"))
    
    company = Company.query.get_or_404(id)
    joined_date = company.created_at.strftime("%d %b %Y")
    ongoing_drives = PlacementDrive.query.filter_by(company_id=id, status="Approved").all()
    closed_drives = PlacementDrive.query.filter_by(company_id=id, status="Closed").all()
    
    return render_template("admin/company_detail.html",
        company=company,
        joined_date=joined_date,
        ongoing_drives=ongoing_drives,
        closed_drives=closed_drives
    )

@app.route("/admin/drive/<int:id>")
def admin_drive_detail(id):
    if "user_id" not in session or session["role"] != "admin":
        flash("Please login as Admin", "danger")
        return redirect(url_for("admin_login"))
    
    drive = PlacementDrive.query.get_or_404(id)
    applications = Application.query.filter_by(drive_id=id).all()
    
    return render_template("admin/drive_detail.html",
        drive=drive,
        applications=applications
    )

@app.route("/admin/application/<int:id>")
def admin_application_detail(id):
    if "user_id" not in session or session["role"] != "admin":
        flash("Please login as Admin", "danger")
        return redirect(url_for("admin_login"))
    application = Application.query.get_or_404(id)
    return render_template("admin/application_detail.html",
        application=application
    )
#####################################################################################3

#LogOut
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully","success")
    return redirect(url_for("login"))

#####################################################################################

### COMPANY ROUTESS ####
#Company Dashboard
@app.route("/company/dashboard")
def company_dashboard ():
    if "user_id" not in session or session ["role"] != "company":
        flash("Please login as Company", "danger")
        return redirect(url_for(" login"))
    company = Company.query.get(session["user_id"])
    drives = PlacementDrive.query.filter_by(company_id=company.id).all()
    total_drives = len(drives)
    total_applications = sum(len(d.applications) for d in drives)
    return render_template("company/dashboard.html",
        company= company,
        drives =drives,
        total_drives=total_drives,
        total_applications= total_applications
    )


@app.route("/company/drive/create", methods=["GET", "POST"])
def company_create_drive():
    if "user_id" not in session or session["role"] != "company":
        flash("Please login as Company", "danger")
        return redirect(url_for("login"))
    company = Company.query.get(session["user_id"])
    if request.method == "POST":
        job_title =request.form.get("job_title", "")
        job_description=request.form.get("job_description", "")
        eligibility= request.form.get("eligibility", "")
        salary = request.form.get("salary", "")
        location= request.form.get("location", "")
        deadline_str = request.form.get("deadline", "")
        deadline =datetime.strptime(deadline_str, "%Y-%m-%d").date() if deadline_str else None
        drive = PlacementDrive(
            company_id=company.id,
            job_title=job_title,
            job_description=job_description,
            eligibility=eligibility,
            salary=salary,
            location=location,
            deadline=deadline,
            status="Pending"
        )
        db.session.add(drive)
        db.session.commit()
        flash("Drive created! Waiting for admin approval.", "success")
        return redirect(url_for("company_dashboard"))
    return render_template("company/create_drive.html", company=company)


@app.route("/company/drive/<int:id>/edit", methods=["GET", "POST"])
def company_edit_drive(id):
    if "user_id" not in session or session["role"] != "company":
        flash("Please login as Company", "danger")
        return redirect(url_for("login"))
    company = Company.query.get(session["user_id"])
    drive = PlacementDrive.query.get_or_404(id)
    if drive.company_id != company.id:
        flash("Unauthorized access!", "danger")
        return redirect(url_for("company_dashboard"))
    if request.method == "POST":
        drive.job_title = request.form.get ("job_title", "")
        drive.job_description =request.form.get("job_description", "")
        drive.eligibility=request.form.get("eligibility", "")
        drive.salary = request.form.get("salary", "")
        drive.location = request.form.get("location", "")
        deadline_str= request.form.get("deadline", "")
        drive.deadline=datetime.strptime(deadline_str, "%Y-%m-%d").date() if deadline_str else None
        db.session.commit()
        flash("Drive updated successfully!", "success")
        return redirect(url_for("company_dashboard"))
    return render_template ("company/edit_drive.html", company=company, drive=drive)


@app.route("/company/drive/<int:id>/close")
def company_close_drive(id):
    if "user_id" not in session or session["role"] != "company":
        flash("Please login as Company", "danger")
        return redirect(url_for("login"))
    company = Company.query.get(session["user_id"])
    drive = PlacementDrive.query.get_or_404(id)
    if drive.company_id!=company.id:
        flash("Unauthorized access!", "danger")
        return redirect(url_for("company_dashboard" ) )
    drive.status = "Closed"
    db.session.commit()
    flash("Drive closed successfully.", "info")
    return redirect(url_for("company_dashboard") )


@app.route("/company/drive/<int:id>/applicants")
def company_applicants(id):
    if "user_id" not in session or session["role"] != "company":
        flash("Please login as Company", "danger")
        return redirect(url_for("login"))
    company = Company.query.get(session["user_id"])
    drive = PlacementDrive.query.get_or_404(id)
    if drive.company_id != company.id:
        flash("Unauthorized access!", "danger")
        return redirect(url_for("company_dashboard"))
    applications = Application.query.filter_by(drive_id=id).all()
    return render_template("company/applicants.html",
        company=company,
        drive=drive,
        applications=applications
    )


@app.route("/company/application/<int:id>/review", methods=["GET", "POST"])
def company_review_application(id):
    if "user_id" not in session or session["role"] != "company":
        flash("Please login as Company", "danger")
        return redirect(url_for("login"))
    company = Company.query.get(session["user_id"])
    application = Application.query.get_or_404(id)
    if application.drive.company_id != company.id:
        flash("Unauthorized access!", "danger")
        return redirect(url_for("company_dashboard"))
    if request.method == "POST":
        application.status = request.form.get("status", "Applied")
        db.session.commit()
        flash("Application status updated!", "success")
        return redirect(url_for("company_applicants", id=application.drive_id))
    return render_template ("company/review_application.html",
        company=company,
        application=application
    )

###   STUDENT AREAA!!  #######
@app.route("/student/dashboard")
def student_dashboard():
    if "user_id" not in session or session["role"] != "student":
        flash("Please login as Student", "danger")
        return redirect(url_for("login"))
    student = Student.query.get(session["user_id"])
    approved_drives = PlacementDrive.query.filter_by(status="Approved").all()
    applications = Application.query.filter_by(student_id=student.id).all()
    return render_template("student/dashboard.html",
        student=student,
        approved_drives=approved_drives,
        applications=applications
    )


@app.route("/student/drive/<int:id>")
def student_drive_detail(id):
    if "user_id" not in session or session["role"] != "student":
        flash("Please login as Student", "danger")
        return redirect(url_for("login"))
    student = Student.query.get(session["user_id"])
    drive = PlacementDrive.query.get_or_404(id)
    existing = Application.query.filter_by(
        student_id=student.id,
        drive_id=id
    ).first()
    return render_template("student/drive_detail.html",
        student=student,
        drive=drive,
        existing=existing
    )


@app.route("/student/drive/<int:id>/apply", methods=["POST"])
def student_apply(id):
    if "user_id" not in session or session["role"] != "student":
        flash("Please login as Student", "danger")
        return redirect(url_for("login"))
    student = Student.query.get(session["user_id"])
    drive = PlacementDrive.query.get_or_404(id)
    existing = Application.query.filter_by(
        student_id=student.id,
        drive_id=id
    ).first()
    if existing:
        flash("You have already applied for this drive!", "warning")
        return redirect(url_for("student_dashboard"))
    if drive.status != "Approved":
        flash("This drive is not available!", "danger")
        return redirect(url_for("student_dashboard"))
    application = Application(
        student_id=student.id,
        drive_id=id,
        status="Applied"
    )
    db.session.add(application)
    db.session.commit()
    flash("Applied successfully!", "success")
    return redirect(url_for("student_applications"))


@app.route("/student/applications")
def student_applications():
    if "user_id" not in session or session["role"] != "student":
        flash("Please login as Student", "danger")
        return redirect(url_for("login"))
    student = Student.query.get(session["user_id"])
    applications = Application.query.filter_by(student_id=student.id).all()
    return render_template("student/applications.html",
        student=student,
        applications=applications
    )


@app.route("/student/profile", methods=["GET", "POST"])
def student_profile():
    if "user_id" not in session or session["role"] != "student":
        flash("Please login as Student", "danger")
        return redirect(url_for("login"))
    student = Student.query.get(session["user_id"])
    if request.method == "POST":
        student.name = request.form.get("name", "")
        student.phone = request.form.get("phone", "")
        student.degree = request.form.get("degree", "")
        student.branch = request.form.get("branch", "")
        student.cgpa = float(request.form.get("cgpa", 0))
        resume = request.files.get("resume")
        if resume and resume.filename != "":
            filename = secure_filename(resume.filename)
            resume_folder = os.path.join(app.config["UPLOAD_FOLDER"], "resumes")
            os.makedirs(resume_folder, exist_ok=True)
            resume.save(os.path.join(resume_folder, filename))
            student.resume = filename
        db.session.commit()
        flash("Profile updated successfully!", "success")
        return redirect(url_for("student_profile"))
    return render_template("student/profile.html", student=student)

#########################################################3

@app.route("/upload/resumes/<filename>")
def uploaded_resume(filename):
    return send_from_directory("static/upload/resumes", filename)

@app.route("/upload/certificates/<filename>")
def uploaded_certificate(filename):
    return send_from_directory("static/upload/certificates", filename)


if __name__=="__main__":
    app.run(debug=True)

                
