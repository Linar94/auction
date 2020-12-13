import datetime

from pydantic import BaseModel
from typing import Optional
from fastapi import Body


class AuctionListParams(BaseModel):
    state: Optional[str] = None


class AuctionDetailParams(BaseModel):
    auction: int


class AuctionCreateParams(BaseModel):
    name: str
    price: int
    step: int
    end_dt: datetime.datetime


class BetCreateParams(BaseModel):
    auction: int
    price: int






