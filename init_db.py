from app import app , db
from models import Admin
from werkzeug.security import generate_password_hash

with app.app_context():
    db.create_all()

    admin=Admin.query.filter_by(username="admin").first()

    if not admin:
        hashed_pass=generate_password_hash("admin123")
        admin=Admin(username="admin",password=hashed_pass)
        db.session.add(admin)
        db.session.commit()
        print("Databse created Successfully...\nPrint Admin account created..")
        print("Username : admin\n Password : admin123")
    else:
        print("Database already exist..\nAdmin Already exist!!")
    