from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

main = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Свободный агент👤')],
    [KeyboardButton(text='Клуб🏟️'), KeyboardButton(text='Трансферы📜')],
    [KeyboardButton(text='Лига🏆')],
    [KeyboardButton(text='Сосать у шейхов🔞')]
],
    resize_keyboard=True,
    input_field_placeholder='Выберете пункт меню👇'
)

main_admin = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Свободный агент👤')],
    [KeyboardButton(text='Клуб🏟️'), KeyboardButton(text='Трансферы📜')],
    [KeyboardButton(text='Лига🏆')],
    [KeyboardButton(text='Админ меню😎'), KeyboardButton(text='Сосать у шейхов🔞')]
],
    resize_keyboard=True,
    input_field_placeholder='Выберете пункт меню👇'
)

admin_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Поиск пользователя по TG ID 🔍')],
    [KeyboardButton(text='Выдача 📩')],
    [KeyboardButton(text='Добавить карту ➕'), KeyboardButton(text='Редактировать карту ⚙️')],
    [KeyboardButton(text='Назад 🚪')]
],
    resize_keyboard=True,
    input_field_placeholder='Выберете пункт меню👇')

admin_values = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Крутки (Свободный агент 👤)', callback_data='giving_spins')],
    [InlineKeyboardButton(text='Деньги 💵', callback_data='giving_cash'),
     InlineKeyboardButton(text='Карта 🎴', callback_data='giving_card')], 
    [InlineKeyboardButton(text='Назад 🚪', callback_data='giving_back')]
])

positions = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Вратарь🧤', callback_data='position_goalkeeper')],
    [InlineKeyboardButton(text='Л. Защитник🛡', callback_data='position_left-back'), 
     InlineKeyboardButton(text='Ц. Защитник🛡', callback_data='position_center-back'), 
     InlineKeyboardButton(text='П. Защитник🛡', callback_data='position_right-back')],
    [InlineKeyboardButton(text='Опорный полузащитник🏃‍♂️', callback_data='position_defensive-midfielder')],
    [InlineKeyboardButton(text='Атакующий полузащитник🏃‍♂️', callback_data='position_attacking-midfielder')], 
    [InlineKeyboardButton(text='Нападающий🗡', callback_data='position_forward')],
    [InlineKeyboardButton(text='Вернутся 🚪', callback_data='position_back')]
])

def club_confirmation(best_match):
    buttons = []
    buttons.append([InlineKeyboardButton(text=f"✅ {best_match}", callback_data=f"club_{best_match}")])
    buttons.append([InlineKeyboardButton(text="🆕 Ввести заново", callback_data="club_again")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def nationality_confirmation(best_match):
    buttons = []
    buttons.append([InlineKeyboardButton(text=f"✅ {best_match}", callback_data=f"nationality_{best_match}")])
    buttons.append([InlineKeyboardButton(text="🆕 Ввести заново", callback_data="nationality_again")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def name_confirmation(best_match):
    buttons = []
    buttons.append([InlineKeyboardButton(text=f"✅ {best_match}", callback_data=f"nameforsearch_{best_match}")])
    buttons.append([InlineKeyboardButton(text="🆕 Ввести заново", callback_data="nameforsearch_again")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

delite_card = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Подтвердить ✅', callback_data='delite_card_true')],
    [InlineKeyboardButton(text='Отменить ❌', callback_data='delite_card_false')]
])

options_for_change = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Ред. имя", callback_data="edit_name"),
     InlineKeyboardButton(text="Ред. рейтинг", callback_data="edit_rating")],
    [InlineKeyboardButton(text="Ред. позицию", callback_data="edit_position"),
     InlineKeyboardButton(text="Ред. клуб", callback_data="edit_club")],
    [InlineKeyboardButton(text="Ред. национальность", callback_data="edit_nationality"),
     InlineKeyboardButton(text="Ред. картинку", callback_data="edit_file_id")],
    [InlineKeyboardButton(text="Удалить карту 🗑️", callback_data="edit_delete_card"),
     InlineKeyboardButton(text="Назад 🚪", callback_data="card_editing_back")]
])

search_options = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Поиск по ID/Полному имени", callback_data="ID_full_name")],
    [InlineKeyboardButton(text="Поиск по Примерному имени", callback_data="approximately_name")]
    # [InlineKeyboardButton(text="Поиск по Категориям", callback_data="categories")]
])

def search_parameters():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text="Позиция", callback_data="position")],
    [InlineKeyboardButton(text="Мин. рейтинг", callback_data="min_rating"),
    InlineKeyboardButton(text="Макс. рейтинг", callback_data="max_rating")],
    [InlineKeyboardButton(text="Клуб", callback_data="club")],
    [InlineKeyboardButton(text="Национальность", callback_data="nationality")],
    [InlineKeyboardButton(text="Очистить 🗑️", callback_data="clear"),
     InlineKeyboardButton(text="ПОИСК 🔎", callback_data="search")],
    [InlineKeyboardButton(text="Назад 🚪", callback_data="close_search")]
                                                    ])
    return keyboard
    
def countries_buttons(countries):
    buttons = []
    row = []  # Временный список для строки из 2 кнопок
    for country in countries:
        country_id = country.id
        country_name = country.name
        row.append(InlineKeyboardButton(text=country_name, callback_data=f'countries_{country_id}'))
        if len(row) == 2:  # Если набрали 2 кнопки, добавляем в общий список
            buttons.append(row)
            row = []  # Очищаем строку для новых кнопок
    # Если осталась одна кнопка без пары, добавляем её
    if row:
        buttons.append(row)
    # Добавляем кнопку "Вернуться" в новую строку
    buttons.append([InlineKeyboardButton(text='Вернуться🚪', callback_data='countries_back')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def clubs_buttons(clubs):
    buttons = []
    row = []
    for club in clubs:
        club_id = club.id
        club_name = club.name
        row.append(InlineKeyboardButton(text=club_name, callback_data=f'clubs_{club_id}_{club_name}'))
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)
    buttons.append([InlineKeyboardButton(text='Вернуться🚪', callback_data='clubs_back')])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

agreement = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Предложить контракт 📃', callback_data='agreement_true')],
    [InlineKeyboardButton(text='Отказаться ❌', callback_data='agreement_false')]
])

break_contract = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Разорвать контракт ❌📃', callback_data='break_contract_true')],
    [InlineKeyboardButton(text='Еще подумать... 💭', callback_data='card_editing_back')]
])

break_contract_ok = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Скатертью дорожка 👋', callback_data='card_editing_back')]
])

my_clube = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Ваши игроки 👕', callback_data='user_cards_list')],
    [InlineKeyboardButton(text='Изменить название клуба ✍️', callback_data='rename')],
    [InlineKeyboardButton(text='Сосать у шейхов 🔞', callback_data='suck_cash')]
])

def cards_buttons(cards, current_page=1):
    max_buttons = 6
    card_buttons = [
        InlineKeyboardButton(text=f"📆{card["card_age"]} | {card["name"]}", callback_data=f'user_card_{card["card_id"]}')
        for card in cards
    ]
    
    while len(card_buttons) < max_buttons:
        card_buttons.append(InlineKeyboardButton(text="_______________", callback_data="user_card_empty"))

    rows = [card_buttons[i:i + 3] for i in range(0, max_buttons, 3)]
    
    # Добавляем кнопки для навигации по страницам
    navigation_buttons = []
    if current_page > 1:
        navigation_buttons.append(InlineKeyboardButton(text='⬅️', callback_data='previous_six'))
    navigation_buttons.append(InlineKeyboardButton(text='➡️', callback_data='next_six'))
    
    rows.append(navigation_buttons)
    rows.append([InlineKeyboardButton(text='Вернуться🚪', callback_data='user_card_back')])
    
    return InlineKeyboardMarkup(inline_keyboard=rows)

