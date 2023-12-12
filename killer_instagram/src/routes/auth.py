
from fastapi import APIRouter, Depends, HTTPException, status, Security, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm, HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session


from src.services.auth import service_auth
from src.database.db import get_db
from src.repository import users as repository_users
from src.schemas import users as schema_users, token as schema_token
from src.services.email import send_email, send_reset_password_email
from src.schemas.email import RequestEmail
from src.schemas.users import ChangePassword, UserRoleUpdate, UserResponce
from src.database.models import User

router = APIRouter(prefix='/auth', tags=['auth'])
security = HTTPBearer()


@router.post('/signup', status_code=status.HTTP_201_CREATED)
async def signup(body: schema_users.UserModel, background_tasks: BackgroundTasks, request: Request, db: Session = Depends(get_db)):
    """
    The signup function creates a new user in the database.
        It also sends an email to the user's email address for verification purposes.
        The function returns a dict containing the newly created user and a detail message.
    
    :param body: schema_users.UserModel: Validate the input data, and it is also used to create a new user
    :param background_tasks: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the application
    :param db: Session: Get the database session,
    :return: A dictionary
    """
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f'User with email: {body.email} already exists')
    body.password = service_auth.get_password_hash(body.password)
    user = await repository_users.create_user(body, db)
    background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {'user': user, 'detail': 'User successfully created, please check your email for verification'}


@router.post("/login", response_model=schema_token.TokenResponce, status_code=status.HTTP_202_ACCEPTED)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    The login function is used to authenticate a user.
    
    :param body: OAuth2PasswordRequestForm: Validate the request body
    :param db: Session: Access the database
    :return: A dictionary
    """
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not user.confirmed:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Email is not confirmed')
    if not service_auth.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    access_token = await service_auth.create_access_token(data={"sub": user.email})
    refresh_token = await service_auth.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/refresh_token', response_model=schema_token.TokenResponce)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), db: Session = Depends(get_db)):
    """
    The refresh_token function is used to refresh the access and refresh tokens.
    It takes in a refresh token and returns an access_token, a new refresh_token, and the type of token (bearer).
    
    
    :param credentials: HTTPAuthorizationCredentials: Get the token from the request header
    :param db: Session: Create a connection to the database
    :return: A dict with the access_token, refresh_token and token type
    """
    token = credentials.credentials
    email = await service_auth.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        user.refresh_token = None
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    access_token = await service_auth.create_access_token(data={"sub": email})
    refresh_token = await service_auth.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirm_email(token: str, db: Session = Depends(get_db)):
    """
    The confirm_email function is used to confirm a user's email address.
        The function takes in the token that was sent to the user's email and decodes it,
        then checks if there is a user with that email address in the database. If there isn't,
        an error message will be returned. If there is, we check if their account has already been confirmed or not. 
        If it has been confirmed already, we return a message saying so; otherwise we update their account as being confirmed.
    
    :param token: str: Get the token from the url
    :param db: Session: Get a database session
    :return: A dict with a message key
    """
    email = await service_auth.decode_email_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Verification error')
    if user.confirmed:
        return {'message': 'Email is already confirmed'}
    await repository_users.confirmed_email(email, db)
    return {'message': 'Email is confirmed'}


@router.post('/request_email', status_code=status.HTTP_202_ACCEPTED)
async def request_email(body: RequestEmail, background_task: BackgroundTasks, 
                        request: Request, db: Session = Depends(get_db)):
    """
    The request_email function is used to send an email to the user with a link
    to confirm their account. The function takes in a RequestEmail object, which 
    contains the user's email address. It then checks if that email address exists 
    in our database and if it does, sends an email containing a confirmation link.
    
    :param body: RequestEmail: Get the email from the request body
    :param background_task: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base url of the application
    :param db: Session: Get the database session
    :return: A string
    """
    user = await repository_users.get_user_by_email(body.email, db)
    if user is not None and user.confirmed:
        return {'message': 'Email is already confirmed'}
    if user:
        background_task.add_task(send_email, user.email, user.username, request.base_url)
    return {'message': 'Check your email for further information'}


@router.post('/reset_password', status_code=status.HTTP_202_ACCEPTED)
async def reset_password_request(body: RequestEmail, background_task: BackgroundTasks,
                          request: Request, db: Session = Depends(get_db)):
    """
    The reset_password_request function is used to send a reset password email to the user.
        The function takes in an email address and sends a reset password link to that address.
        If the user does not exist, then no action is taken.
    
    :param body: RequestEmail: Get the email from the request body
    :param background_task: BackgroundTasks: Add a task to the background tasks queue
    :param request: Request: Get the base_url of the server to be used in the email
    :param db: Session: Get the database session
    :return: A string
    """
    user = await repository_users.get_user_by_email(body.email, db)
    if user:
        background_task.add_task(send_reset_password_email, user.email, user.username, request.base_url)
    return {'message': 'Check your email for further information'}


@router.patch('/change_password/{token}')
async def reset_password(body: ChangePassword, token: str, db: Session = Depends(get_db)):
    """
    The reset_password function is used to reset a user's password.
        It takes in the body of the request, which contains a new_password field, and a token that was sent to the user's email address.
        The function decodes the token using service_auth.decode_email_token(token), and then uses repository_users.get_user_by_email() to get 
        information about that user from our database (db). If no such user exists, we return an HTTPException with status code 400 (Bad Request) 
        and detail 'Verification error'. Otherwise we hash their new password using
    
    :param body: ChangePassword: Get the new password from the request body
    :param token: str: Get the token from the url
    :param db: Session: Get the database session
    :return: A string
    """
    email = await service_auth.decode_email_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Verification error')
    body.new_password = service_auth.get_password_hash(body.new_password)
    await repository_users.change_password(user, body.new_password, db)
    return "User's password was changed succesfully"


@router.patch('/change_role/{user_id}', response_model=UserResponce)
async def change_user_role(
    user_id: int,
    body: UserRoleUpdate,
    current_user: User = Depends(service_auth.get_current_user),
    db: Session = Depends(get_db)
):
    """
    The change_user_role function allows an admin to change the role of a user.
    
    :param user_id: int: Fetch the user by id from the database
    :param body: UserRoleUpdate: Get the new role from the request body
    :param current_user: User: Get the current user from the database
    :param db: Session: Pass the database session to the function
    :return: A user object with udated role
    :doc-author: Trelent
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Permission denied. Only admin can change roles.")
    user = await repository_users.get_user_by_id(user_id, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user.id == user_id:
        raise HTTPException(status_code=403, detail="Permission denied. Own role cannot be changed.")
    if user.id == 1:
        raise HTTPException(status_code=403, detail="Permission denied.Superadmin role cannot be changed.")
    if user.role == "admin" and current_user.id != 1:
        raise HTTPException(status_code=403, detail="Permission denied.Admin role can be changed only by Superadmin (id=1).")

    if body.role in ['admin', 'moderator', 'user']:
        await repository_users.change_user_role(user, body, db)
        return user
    else:
        raise HTTPException(status_code=400, detail="Invalid role provided")
    