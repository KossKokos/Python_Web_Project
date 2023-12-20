from typing import List

from sqlalchemy import Column, Integer, String, ForeignKey, Boolean, func, CheckConstraint, Table
from sqlalchemy.orm import relationship, declarative_base, Mapped
from sqlalchemy.sql.sqltypes import Date, DateTime

Base = declarative_base()
    
"""
Змінюйте, де потрібно, робіть міграції і перевіряйте
"""

class User(Base):
    __tablename__ = "users_table"

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    password = Column(String(100), nullable=False)
    created_at = Column('created_at', DateTime, default=func.now())
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    confirmed = Column(Boolean, default=False)
    role = Column(String(20), nullable=False, default='user')
    banned = Column(Boolean, default=False)
    blacklisted_token = relationship('BlacklistedToken', uselist=False, back_populates='user')
    images = relationship('Image', back_populates='user')

    __table_args__ = (
        CheckConstraint(
            role.in_(['admin', 'moderator', 'user']),
            name='check_valid_role'
        ),
    )

    def __str__(self):
        return str(self.id)


image_m2m_tag = Table(
    "image_m2m_tag",
    Base.metadata,
    Column("id", Integer, primary_key=True),
    Column("image_id", Integer, ForeignKey("images_table.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tags_table.id", ondelete="CASCADE")),
)


class Image(Base):
    __tablename__ = "images_table"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users_table.id"), nullable=False)
    description = Column(String(255))
    upload_time = Column(DateTime(timezone=True), server_default=func.now())
    comments = relationship('Comment', back_populates='image')
    image_url = Column(String)
    public_id = Column(String(255))
    file_extension = Column(String, nullable=False)

    user = relationship("User", back_populates="images")
    tags = relationship("Tag", secondary="image_m2m_tag", back_populates="images")
    transformed_links = relationship("TransformedImageLink", back_populates="image")


class TransformedImageLink(Base):
    __tablename__ = "transformed_image_links"

    id = Column(Integer, primary_key=True)
    image_id = Column(Integer, ForeignKey("images_table.id", ondelete='CASCADE'), nullable=False) # тут, я додав ondelete cascade 
    created_at = Column('created_at', DateTime, default=func.now())
    transformation_url = Column(String(255), nullable=False)
    qr_code_url = Column(String(255), nullable=True, server_default="")

    image = relationship("Image", back_populates="transformed_links")

class Comment(Base):
    __tablename__ = 'comments_table'
    
    id = Column(Integer, primary_key=True)
    comment = Column(String(150), nullable=False)
    created_at = Column('created_at', DateTime, default=func.now())
    updated_at = Column('updated_at', DateTime)
    image_id = Column('image_id', ForeignKey('images_table.id', ondelete='CASCADE'))
    image = relationship('Image', back_populates='comments')


class Tag(Base):
    __tablename__ = 'tags_table'
    
    id = Column(Integer, primary_key=True)
    tag = Column(String(30), nullable=False, unique=True)
    images = relationship('Image', secondary='image_m2m_tag', back_populates='tags')


class BlacklistedToken(Base):
    __tablename__ = 'blacklisted_tokens'
    
    id = Column(Integer, primary_key=True)
    blacklisted_token = Column(String(255), nullable=True)
    user_id = Column('user_id', ForeignKey('users_table.id', ondelete='CASCADE'), unique=True)
    user = relationship('User', back_populates='blacklisted_token')