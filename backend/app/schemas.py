from pydantic import BaseModel, ConfigDict


class BookBase(BaseModel):
    title: str
    author: str
    isbn: str = ""
    genre: str = "general"
    price: float
    available: bool = True


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: str | None = None
    author: str | None = None
    isbn: str | None = None
    genre: str | None = None
    price: float | None = None
    available: bool | None = None


class BookResponse(BookBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
