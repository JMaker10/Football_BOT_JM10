from sqlalchemy import (
    BigInteger, String, ForeignKey, CheckConstraint, Integer, DateTime,
    UniqueConstraint, Enum, Index
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from datetime import datetime

engine = create_async_engine(url='sqlite+aiosqlite:///fbdb.sqlite3')
async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(AsyncAttrs, DeclarativeBase):
    pass


# Перерахування для позицій гравців
position_enum = Enum(
    "goalkeeper", "left-back", "right-back", "center-back",
    "defensive-midfielder", "attacking-midfielder", "forward",
    name="position_enum"
)


class Country(Base):
    __tablename__ = "countries"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    
    clubs: Mapped[list["Club"]] = relationship(back_populates="country")
    leagues: Mapped[list["League"]] = relationship(back_populates="country")

class League(Base):
    __tablename__ = "leagues"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"), nullable=True)
    
    country: Mapped["Country"] = relationship(back_populates="leagues")
    clubs: Mapped[list["Club"]] = relationship(back_populates="league")

class Club(Base):
    __tablename__ = "clubs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    
    league_id: Mapped[int] = mapped_column(ForeignKey("leagues.id"), nullable=False)
    country_id: Mapped[int] = mapped_column(ForeignKey("countries.id"), nullable=False)
    
    league: Mapped["League"] = relationship(back_populates="clubs")
    country: Mapped["Country"] = relationship(back_populates="clubs")
    cards: Mapped[list["Card"]] = relationship(back_populates="club")


class Nationality(Base):
    __tablename__ = "nationalities"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    cards: Mapped[list["Card"]] = relationship(back_populates="nationality")


class UserCardAssociation(Base):
    __tablename__ = "user_card_association"
    __table_args__ = (
        UniqueConstraint("user_id", "card_id", name="uq_user_card"),
        CheckConstraint('card_age >= 18 AND card_age <= 35', name='check_age_range'),
        Index("idx_user_id", "user_id"),
    )

    user_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"), primary_key=True)
    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id"), primary_key=True)
    card_age: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Зв'язки з іншими таблицями
    user: Mapped["User"] = relationship(back_populates="card_associations")
    card: Mapped["Card"] = relationship(back_populates="user_associations")


class User(Base):
    __tablename__ = 'users'

    tg_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, unique=True)
    username: Mapped[str] = mapped_column(String(25), default="Безымянный")
    cash: Mapped[int] = mapped_column(BigInteger, default=50000)
    spins: Mapped[int] = mapped_column(Integer, default=3)
    next_spin: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Зв'язок з асоціаціями
    card_associations: Mapped[list["UserCardAssociation"]] = relationship(
        back_populates="user",
        lazy="selectin"
    )

    @property
    def collection(self):
        """Повертає колекцію у вигляді списку словників {card_id, card_age}."""
        return [
            {"card_id": assoc.card_id, "card_age": assoc.card_age}
            for assoc in self.card_associations
        ]


class Card(Base):
    __tablename__ = 'cards'
    __table_args__ = (
        CheckConstraint('rating >= 1 AND rating <= 100', name='check_rating_range'),
        Index("idx_position", "position"),
        Index("idx_rating", "rating"),
        Index("idx_position_rating", "position", "rating")
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(25))
    rating: Mapped[int] = mapped_column(Integer)
    position: Mapped[str] = mapped_column(position_enum)
    file_id: Mapped[str] = mapped_column(String, nullable=True)

    # Нові поля клубу та національності
    club_id: Mapped[int] = mapped_column(ForeignKey("clubs.id"), nullable=True)
    nationality_id: Mapped[int] = mapped_column(ForeignKey("nationalities.id"), nullable=True)

    # Зв'язок із таблицями Club та Nationality
    club: Mapped["Club"] = relationship(back_populates="cards")
    nationality: Mapped["Nationality"] = relationship(back_populates="cards")

    # Зв'язок із UserCardAssociation
    user_associations: Mapped[list["UserCardAssociation"]] = relationship(back_populates="card")


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
