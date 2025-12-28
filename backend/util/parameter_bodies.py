from pydantic import BaseModel
from pydantic.generics import GenericModel
from typing import Generic, TypeVar, Optional

class CreateGame(BaseModel):
    player_name: str
    game_id: Optional[str] = None

DataT = TypeVar('DataT')

class ResponseEnvelope(BaseModel, Generic[DataT]):
    status: str = "success"
    message: Optional[str] = None
    data: Optional[DataT] = None