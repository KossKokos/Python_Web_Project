from typing import List

from sqlalchemy.orm import Session

from ..database.models import Tag


async def get_or_create_tag(db: Session, tag_name: str) -> Tag:
    """
    The get_or_create_tag function will either return an existing tag from the database, or create a new one if it doesn't exist.
    
    :param db: Session: Connect to the database
    :param tag_name: str: Pass in the tag name
    :return: A tag object
    """
    existing_tag = db.query(Tag).filter(Tag.tag == tag_name).first()

    if existing_tag:
        return existing_tag

    new_tag = Tag(tag=tag_name)
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)

    return new_tag

async def get_existing_tags(db: Session) -> list:
    """
    The get_existing_tags function returns a list of all the tags that are currently in the database.
        
    
    :param db: Session: Pass in the database session
    :return: A list of all the tags in the database
    """
    existing_tags: List[Tag] = db.query(Tag.tag).distinct().all()
    return [tag.tag for tag in existing_tags]


async def get_tag_by_name(tag: str, db: Session) -> Tag | None:
    """
    The get_tag_by_name function returns a tag object from the database if it exists, otherwise None.
    
    :param tag: str: Query the database for a tag with that name
    :param db: Session: Pass the database session to the function
    :return: A tag object or none
    """
    exist_tag = db.query(Tag).filter(Tag.tag==tag).first()
    return exist_tag