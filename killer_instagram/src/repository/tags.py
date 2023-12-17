"""
Тут crud операції тільки над тегами
"""
from sqlalchemy.orm import Session
from src.database.models import Tag

async def get_or_create_tag(db: Session, tag_name: str) -> Tag:
    existing_tag = db.query(Tag).filter(Tag.tag == tag_name).first()

    if existing_tag:
        return existing_tag

    new_tag = Tag(tag=tag_name)
    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)

    return new_tag

async def get_existing_tags(db: Session):
    existing_tags = db.query(Tag.tag).distinct().all()
    return [tag[0] for tag in existing_tags]
