from pydantic import BaseModel


class OrgSignup(BaseModel):
    orgname: str
    email: str
    password: str


class OrgLogin(BaseModel):
    email: str
    password: str