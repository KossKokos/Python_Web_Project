from pydantic import BaseModel


class TokenResponce(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str