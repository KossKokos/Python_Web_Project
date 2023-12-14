from sqlalchemy.orm import Session

from src.database.models import BlacklistedToken 

async def token_to_blacklist(access_token: str, user_id, db: Session):

    result = await is_token_blacklisted (user_id, db)
    print (10, result)
    print (11, access_token)
    token = BlacklistedToken()
    token.user_id =  user_id
    print (14,token.user_id)
    token.blacklisted_token = access_token
    print (16, token.blacklisted_token)
    db.add(token)
    db.commit()
    db.refresh(token)

    return token

async def is_token_blacklisted(user_id, db: Session):
    
    token = db.query(BlacklistedToken).filter(BlacklistedToken.user_id == user_id).first()
    
    if token:
        result = await remove_old_blacklisted_token(token, db)
        print (28, result)
    else:
        return "Ready to write a new blacklist_token"

async def remove_old_blacklisted_token(token: BlacklistedToken, db: Session):
    print (34, token)
    db.delete(token)
    db.commit()
    return "Old blacklist_token removed"
