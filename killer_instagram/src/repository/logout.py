from sqlalchemy.orm import Session

from src.database.models import BlacklistedToken 

async def token_to_blacklist(access_token: str, user_id, db: Session):
    """
    The token_to_blacklist function takes in a token and adds it to the blacklist.
        Args:
            access_token (str): The token that is being blacklisted.
            user_id (int): The id of the user who's token is being blacklisted.
            db (Session, optional): SQLAlchemy Session instance. Defaults to None.&lt;/code&gt;
    
    :param access_token: str: Pass the token to be blacklisted
    :param user_id: Identify the user and the db parameter is used to connect to the database
    :param db: Session: Pass in the database session to the function
    :return: An object of type blacklistedtoken
    :doc-author: Trelent
    """
    result = await is_token_blacklisted (user_id, db)
    token = BlacklistedToken()
    token.user_id =  user_id
    token.blacklisted_token = access_token
    db.add(token)
    db.commit()
    db.refresh(token)
    return token

async def is_token_blacklisted(user_id, db: Session):
    """
    The is_token_blacklisted function checks if a token is blacklisted.
        If the token is blacklisted, it will be removed from the database and 
        replaced with a new one. This function also removes old tokens that have 
        expired.
    
    :param user_id: Find the user in the database
    :param db: Session: Pass in the database session
    :return: "Ready to write a new blacklist_token"
    :doc-author: Trelent
    """
    
    token = db.query(BlacklistedToken).filter(BlacklistedToken.user_id == user_id).first()
    
    if token:
        result = await remove_old_blacklisted_token(token, db)
        return result
    else:
        return "Ready to write a new blacklist_token"

async def remove_old_blacklisted_token(token: BlacklistedToken, db: Session):
    db.delete(token)
    db.commit()
    return "Old blacklist_token removed"
