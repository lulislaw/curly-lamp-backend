from pydantic import BaseModel


class AppealTypeRead(BaseModel):
    id: int
    code: str
    name: str

    class Config:
        from_attributes = True


class SeverityLevelRead(BaseModel):
    id: int
    code: str
    name: str
    priority: int

    class Config:
        from_attributes = True


class AppealStatusRead(BaseModel):
    id: int
    code: str
    name: str

    class Config:
        from_attributes = True
