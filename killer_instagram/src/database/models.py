from typing import List

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, func, CheckConstraint, DateTime
from sqlalchemy.orm import relationship, declarative_base, Mapped
from sqlalchemy.sql.sqltypes import Date, DateTime

from datetime import datetime
from database import Base


Base = declarative_base()
    
"""
Змінюйте, де потрібно, робіть міграції і перевіряйте
"""

class CommentDB(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user_id = Column(Integer, ForeignKey("users.id"))
    image_id = Column(Integer, ForeignKey("images.id"))

    author = relationship("User", back_populates="comments")
    image = relationship("Image", back_populates="comments")


class User(Base):
    __tablename__ = "users_table"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    created_at = Column('created_at', DateTime, default=func.now())
    pictures = relationship('Picture', back_populates='user')
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


class Picture(Base):
    __tablename__ = 'pictures_table'

    id = Column(Integer, primary_key=True)
    description = Column(String(150), nullable=True)
    url = Column(String(255), nullable=False)
    user_id = Column('user_id', ForeignKey('users_table.id', ondelete='CASCADE'))
    comments = relationship('Comment', back_populates='picture')
    tags = relationship('Tag', back_populates='picture')
    user = relationship('User', back_populates='pictures')


class Comment(Base):
    __tablename__ = 'comments_table'
    
    id = Column(Integer, primary_key=True)
    comment = Column(String(150), nullable=False)
    created_at = Column('crated_at', DateTime, default=func.now())
    updated_at = Column('updated_at', DateTime)
    picture_id = Column('picture_id', ForeignKey('pictures_table.id', ondelete='CASCADE'))
    picture = relationship('Picture', back_populates='comments')


class Tag(Base):
    __tablename__ = 'tags_table'
    
    id = Column(Integer, primary_key=True)
    tag = Column(String(30), nullable=False, unique=True)
    picture_id = Column('picture_id', ForeignKey('pictures_table.id', ondelete='CASCADE'))
    picture = relationship('Picture', back_populates='tags')
