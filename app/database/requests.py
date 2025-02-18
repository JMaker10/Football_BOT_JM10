from sqlalchemy import select, func, desc
import random
from datetime import datetime, timedelta
from typing import Optional, List

from app.database.models import async_session
from app.database.models import User, UserCardAssociation, Card, Club, Nationality, Country

import app.drop_settings as ds


async def set_user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            session.add(User(tg_id=tg_id))
            await session.commit()



async def user(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
    return user



async def spin_spending(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id)) 
        if user.spins - 1 >= 0:
            user.spins = user.spins - 1
            await session.commit()
            return True
        else:
            return False

async def spins_add(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id)) 
        user.spins += 1
        await session.commit()

async def three_spins_check(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id)) 
        if user.spins >= 3:
            return False
        else:
            return True



async def add_some_spins(tg_id, spins_amount):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id)) 
        user.spins += spins_amount
        await session.commit()

async def add_some_cash(tg_id, cash_amount):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id)) 
        user.cash += cash_amount
        await session.commit()


async def remove_cash(user_id, penalty_amount):
    async with async_session() as session:
        # Пошук користувача
        user = await session.scalar(select(User).where(User.tg_id == user_id))
        user.cash += penalty_amount
        await session.commit()


async def next_spin(tg_id):
    async with async_session() as session: 
        user = await session.scalar(select(User).where(User.tg_id == tg_id))        
        next_spin = datetime.now() + timedelta(minutes=1)
        user.next_spin = next_spin
        await session.commit()
        return next_spin

async def get_random_card():
    async with async_session() as session: 
        card_age, card_rating, card_price, discount = await ds.free_agent_card_age_rating_price()
        result = await session.execute(select(Card).where(Card.rating == card_rating))
        cards = result.scalars().all()
        if cards:
            random_card = random.choice(cards)
            return random_card, card_age, card_price, discount
        else:
            return None 



async def suck_cash(tg_id):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        values = [1000, 3000, 5000, 20000]
        profit = random.choice(values)
        user.cash += profit
        await session.commit()
    return profit



async def add_card_to_user(tg_id, card_id, card_age, card_price):
    async with async_session() as session:
        # Пошук користувача
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        result = 0
        existing_association = await session.execute(
            select(UserCardAssociation).filter_by(user_id=user.tg_id, card_id=card_id)
        )
        if not existing_association.scalars().first():
            cash_change = user.cash - card_price
            if cash_change > 0:
                association = UserCardAssociation(user_id=user.tg_id, card_id=card_id, card_age=card_age)
                session.add(association)
                user.cash = cash_change
                await session.commit()
                result = 1
            else:
                result = cash_change
    return result

async def remove_card_from_user(user_id, card_id):
    async with async_session() as session:
        user_card_association = await session.scalar(select(UserCardAssociation).where(UserCardAssociation.user_id == user_id, UserCardAssociation.card_id == card_id))
        await session.delete(user_card_association)
        await session.commit()
    return

async def add_card_to_user_admin(tg_id, card_id, card_age):
    async with async_session() as session:
        # Пошук користувача
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        result = 0
        existing_association = await session.execute(
            select(UserCardAssociation).filter_by(user_id=user.tg_id, card_id=card_id)
        )
        if not existing_association.scalars().first():
            association = UserCardAssociation(user_id=user.tg_id, card_id=card_id, card_age=card_age)
            session.add(association)
            await session.commit()
            result = 1
    return result


async def get_all_countries():
    async with async_session() as session:
        result = await session.execute(select(Country))
        countries = result.scalars().all()
        return countries
    
async def clubs_from_country(country_id):
    async with async_session() as session:
        result = await session.execute(select(Club).where(Club.country_id == country_id))
        clubs = result.scalars().all()
        return clubs


async def search_user_cards(
    user_id: int,
    min_rating: Optional[int] = None,
    max_rating: Optional[int] = None,
    position: Optional[str] = None,
    club_id: Optional[int] = None,
    nationality_id: Optional[int] = None,
    limit: int = 6,
    offset: int = 0,
    **kwargs
) -> List[dict]:
    async with async_session() as session:
        stmt = (
            select(Card, UserCardAssociation.card_age)
            .join(UserCardAssociation, Card.id == UserCardAssociation.card_id)
            .where(UserCardAssociation.user_id == user_id)
        )

        if min_rating is not None:
            stmt = stmt.where(Card.rating >= min_rating)
        if max_rating is not None:
            stmt = stmt.where(Card.rating <= max_rating)
        if position:
            stmt = stmt.where(Card.position == position)
        if club_id:
            stmt = stmt.where(Card.club_id == club_id)
        if nationality_id:
            stmt = stmt.where(Card.nationality_id == nationality_id)

        stmt = stmt.order_by(desc(Card.rating)).limit(limit).offset(offset)

        result = await session.execute(stmt)
        cards_with_ages = [
            {
                "card_id": card.id,
                "name": card.name,
                "rating": card.rating,
                "position": card.position,
                "club_id": card.club_id,
                "nationality_id": card.nationality_id,
                "file_id": card.file_id,
                "card_age": card_age  # Возраст карточки
            }
            for card, card_age in result.all()
        ]

        return cards_with_ages
    

# async def search_cards_admin(
#     min_rating: Optional[int] = None,
#     max_rating: Optional[int] = None,
#     position: Optional[str] = None,
#     club_id: Optional[int] = None,
#     nationality_id: Optional[int] = None,
#     limit: int = 6,
#     offset: int = 0,
#     **kvargs
# ) -> List[dict]:

#     async with async_session() as session:
#         stmt = select(Card)

#         if min_rating is not None:
#             stmt = stmt.where(Card.rating >= min_rating)
#         if max_rating is not None:
#             stmt = stmt.where(Card.rating <= max_rating)
#         if position:
#             stmt = stmt.where(Card.position == position)
#         if club_id:
#             stmt = stmt.where(Card.club_id == club_id)
#         if nationality_id:
#             stmt = stmt.where(Card.nationality_id == nationality_id)

#         stmt = stmt.order_by(desc(Card.rating))
#         stmt = stmt.limit(limit).offset(offset)

#         result = await session.execute(stmt)
#         cards = result.scalars().all()

#         # Преобразуем объекты Card в словари
#         return [
#             {
#                 "id": card.id,
#                 "name": card.name,
#                 "rating": card.rating,
#                 "position": card.position,
#                 "club_id": card.club_id,
#                 "nationality_id": card.nationality_id,
#                 "file_id": card.file_id  # Добавляем file_id, если есть
#             }
#             for card in cards
#         ]
    
async def rename(tg_id, new_name):
    async with async_session() as session:
        try:
            user = await session.scalar(select(User).where(User.tg_id == tg_id))
            if not user:
                return "not_found"  # Пользователь не найден
            
            user.username = new_name
            await session.commit()
            return "success"  # Успешное обновление
            
        except SQLAlchemyError as e:
            await session.rollback()  # Откат изменений при ошибке
            print(f"Ошибка БД: {e}")
            return "error"  # Ошибка при изменении данных


async def get_all_clubs() -> list:
    """Возвращает список всех названий клубов из базы данных."""
    async with async_session() as session:
        result = await session.execute(select(Club.name))
        return [row[0] for row in result.fetchall()]
    
async def get_club_by_name(name):
    async with async_session() as session:
        result = await session.execute(select(Club).filter(Club.name == name))
        return result.scalars().first()
    
async def get_club_by_id(id):
    async with async_session() as session:
        result = await session.execute(select(Club).filter(Club.id == id))
        return result.scalars().first()


async def get_all_nationalities() -> list:
    """Возвращает список всех национальностей из базы данных."""
    async with async_session() as session:
        result = await session.execute(select(Nationality.name))
        return [row[0] for row in result.fetchall()]
    
async def get_nationality_by_name(name):
    async with async_session() as session:
        result = await session.execute(select(Nationality).filter(Nationality.name == name))
        return result.scalars().first()

async def get_nationality_by_id(id):
    async with async_session() as session:
        result = await session.execute(select(Nationality).filter(Nationality.id == id))
        return result.scalars().first()    


async def search_card_by_id(card_id):
    async with async_session() as session:
        card = await session.scalar(select(Card).where(Card.id == card_id))
    return card


async def user_card_association_by_user_card(user_id, card_id):
    async with async_session() as session:
        user_card_association = await session.scalar(select(UserCardAssociation).where(UserCardAssociation.user_id == user_id, UserCardAssociation.card_id == card_id))
    return user_card_association


async def get_all_cards_names() -> list:
    """Возвращает список всех национальностей из базы данных."""
    async with async_session() as session:
        result = await session.execute(select(Card.name))
        return [row[0] for row in result.fetchall()]

async def search_card_by_name(card_name):
    async with async_session() as session:
        card = await session.scalar(select(Card).where(Card.name == card_name))
    return card

async def add_new_card(name, rating, position, file_id, club, nationalit):
    async with async_session() as session:
        new_card = Card(
        name=name,
        rating=rating,
        position=position,
        file_id=file_id,
        club=club,
        nationality=nationalit
    )
    session.add(new_card)
    await session.commit()

async def update_card_name(card_id, new_name):
    async with async_session() as session:
        try:
            result = await session.execute(select(Card).where(Card.id == card_id))
            card = result.scalars().first()
            card.name = new_name
            await session.commit()
            return True
        except:
            return False
        
async def update_card_rating(card_id, new_rating):
    async with async_session() as session:
        result = await session.execute(select(Card).where(Card.id == card_id))
        card = result.scalars().first()
        card.rating = new_rating
        await session.commit()

async def update_card_position(card_id, new_position):
    async with async_session() as session:
        result = await session.execute(select(Card).where(Card.id == card_id))
        card = result.scalars().first()
        card.position = new_position
        await session.commit()

async def update_card_club(card_id, new_club):
    async with async_session() as session:
        result = await session.execute(select(Card).where(Card.id == card_id))
        card = result.scalars().first()
        card.club = new_club
        await session.commit()

async def update_card_nationality(card_id, new_nationality):
    async with async_session() as session:
        result = await session.execute(select(Card).where(Card.id == card_id))
        card = result.scalars().first()
        card.nationality = new_nationality
        await session.commit()

async def update_card_file_id(card_id, new_file_id):
    async with async_session() as session:
        result = await session.execute(select(Card).where(Card.id == card_id))
        card = result.scalars().first()
        card.file_id = new_file_id
        await session.commit()

async def delete_card(card_id):
    async with async_session() as session:
        result = await session.execute(select(Card).where(Card.id == card_id))
        card = result.scalars().first()
        if card:
            await session.delete(card)
            await session.commit()



    