from typing import List

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, func
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql.sqltypes import DateTime

Base = declarative_base()
    

class User(Base):
    __tablename__ = "users_table"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    created_at = Column('crated_at', DateTime, default=func.now())
    pictures = relationship('Picture', back_populates='user')
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)


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