import os
import smtplib
import secrets
import string
from email.mime.text import MIMEText

from app import db, r
from models.user import User

class UserService:
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    APP_PASSWORD = os.getenv("APP_PASSWORD")
    
    @staticmethod
    def get_user_by_id(user_id):
        return User.query.get(user_id)
    
    @staticmethod
    def create_user(email, username, password, role = "Member", status = "Active"):
        if User.query.filter_by(email):
            return None, "Email already exist"
        if User.query.filter_by(username):
            return None, "Username already exist"
        if len(password) < 8:
            return None, "The minimum length of the password must be 8"
        user = User(username = username, email = email, role = role, status = status)
        user.set_password(password=password)
        db.session.add(user)
        db.session.commit()
    @staticmethod
    def get_user_by_email(email):
        return User.query.filter_by(email = email).first()
    @staticmethod
    def get_user_by_username(username):
        return User.query.filter_by(username=username).first()
    @staticmethod
    def get_user_by_name_or_email(email_username):
        user = User.query.filter_by(username = email_username).first()
        if not user:
            user = User.query.filter_by(email = email_username).first()
        return user
    @staticmethod
    def get_all_users():
        return User.query.all()
    @staticmethod
    def update_user_by_member(user_id, data):
        user = UserService.get_user_by_id(user_id)
        if not user:
            return None, "User not exist"
        if 'username' in data:
            exist_username = User.query.filter(User.username == data['username'], User.user_id != user_id).first()
            if exist_username:
                return None, "New username exist"
            user.username  = data['username']
        if 'password' in data:
            if len(data['password']) < 8:
                return None, "The minimum length of the password must be 8"
            user.set_password(data['password'])
        db.session.commit()
        return user, None
    @staticmethod
    def delete_user(user_id):
        user = UserService.get_user_by_id(user_id)
        if not user:
            return False, "User not found"
        db.session.delete(user)
        db.session.commit()
        return True, "User deleted successfully"
    @staticmethod
    def toggle_user_lock(user_id):
        user = UserService.get_user_by_id(user_id)
        if not user:
            return None, "User not found"
        if user.status == "Active":
            user.status = "Locked"
        else:
            user.status = "Active"
        db.session.commit()
        return user, None
    @staticmethod
    def send_reset_otp(email):
        user = UserService.get_user_by_email(email=email)
        if not user:
            return False, "User not found"
        otp = ''.join(secrets.choice(string.digits) for _ in range(6))
        r.setex(f"otp: {email}", 300, otp)
        
        try:
            subject = "Your OTP Code"
            body = f"Your OTP code is: {otp}. It will expire in 5 minutes."
            msg = MIMEText(body, "plan", "utf-8")
            msg["Subject"] = subject
            msg["From"] = UserService.SENDER_EMAIL
            msg["To"] = email
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(UserService.SENDER_EMAIL, UserService.APP_PASSWORD)
                server.sendmail(UserService.SENDER_EMAIL, email, msg.as_string())
            return True, "OTP has been sent to your email."
        except Exception as e:
            print(f"ERROR sending email: {e}")
            return False, "Failed to send OTP email."
    @staticmethod
    def verify_otp_and_reset_password(email, input_otp, new_password):
        saved_otp = r.get(f"otp:{email}")
        if not saved_otp or input_otp != saved_otp:
            return False, "Invalid or expired OTP"
        user = UserService.get_user_by_email(email=email)
        if not user:
            return False, "User not found"
        user.set_password(new_password)
        db.session.commit()
        r.delete(f"otp:{email}")
        return True, "Password has been reset successfully."