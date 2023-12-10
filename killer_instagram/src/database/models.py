from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, func, CheckConstraint
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql.sqltypes import Date, DateTime

Base = declarative_base()

# class Role(Base):
#     admin = Column(String(50), nullable=False, default = "admin")
#     moderator = Column(String(50), nullable=False, default = "moderator")
#     user = Column(String(50), nullable=False, default = "user")
    

# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True)
#     username = Column(String(50), nullable=False)
#     email = Column(String(100), nullable=False, unique=True)
#     password = Column(String(100), nullable=False)
#     created_at = Column('crated_at', DateTime, default=func.now())
#     avatar = Column(String(255), nullable=True)
#     refresh_token = Column(String(255), nullable=True)
#     confirmed = Column(Boolean, default=False)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    created_at = Column('created_at', DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    role = Column(String(20), nullable=False, default='user')

    __table_args__ = (
        CheckConstraint(
            role.in_(['admin', 'moderator', 'user']),
            name='check_valid_role'
        ),
    )
    def __str__(self):
        return str(self.id)