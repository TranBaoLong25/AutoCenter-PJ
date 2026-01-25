from app import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __table__ = "users"
    
    user_id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    username = db.Column(db.String(100), unique=True, nullable = False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable = False)
    role = db.Column(db.Enum('Member', 'Admin', 'Staff', name = 'user_roles'), default = "Member")
    status = db.Column(db.Enum('Active', 'Locked', name='user_statuses'), default = "Active")
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)