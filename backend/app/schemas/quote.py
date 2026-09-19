from pydantic import BaseModel, Field


class QuoteRequest(BaseModel):
    start: str
    end: str
    persist: bool = True


class FlatFareRequest(BaseModel):
    start: str = Field(min_length=1)
    end: str = Field(min_length=1)
    price: float = Field(ge=0)
