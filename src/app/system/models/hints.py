from sqlmodel import Field, SQLModel


class Hint(SQLModel, table=True):
    __tablename__: str = 'hints'

    id: int = Field(primary_key=True)
    posX: int
    posY: int
    hint_fr: str
    hint_en: str
    hint_es: str
    hint_de: str
    hint_pt: str
