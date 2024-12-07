from pydantic import BaseModel

class RecipientResponseData(BaseModel):
    statusCode: int
    number: str
    status: str
    cost: str
    messageId: str

class SMSMessageResponseData(BaseModel):
    Message: str
    Recipients: list[RecipientResponseData]