import streamlit as st
from db_connection import get_filtered_clubs, get_unique_values, get_players_by_club, \
    get_trophies_by_club, get_clubs_by_trophy, get_clubs_by_country, get_clubs, get_trophies, get_country, \
    get_db_connection
from agg_func import players_count, trophies_count, trophywinners_count, clubsincountry_count



def logout():
    st.session_state["logged_in"] = False
    st.session_state["username"] = None


def main_page(role):
    st.sidebar.title(f"Добро пожаловать, {st.session_state['username']}!")
    st.sidebar.button("Выйти", on_click=logout)
    if role == 'user':
        page = st.sidebar.radio("Выберите страницу", ("Фильтрация клубов", "Дополнительная информация"))

        if page == "Фильтрация клубов":
            display_club_filtering()
        elif page == "Дополнительная информация":
            display_additional_info()
    elif role == "reporter":
        page = st.sidebar.radio("Выберите страницу", (
            "Фильтрация клубов", "Дополнительная информация", "Добавить трофей клубу"))

        if page == "Фильтрация клубов":
            display_club_filtering()
        elif page == "Дополнительная информация":
            display_additional_info()
        elif page == "Добавить трофей клубу":
            add_trophy_to_club()
    elif role == 'admin':
        page = st.sidebar.radio("Выберите страницу", ("Фильтрация клубов",
                                                      "Дополнительная информация", "Добавить трофей клубу",
                                                      "Оформить трансфер игрока в другой клуб"))

        if page == "Фильтрация клубов":
            display_club_filtering()
        elif page == "Дополнительная информация":
            display_additional_info()
        elif page == "Добавить трофей клубу":
            add_trophy_to_club()
        elif page == "Оформить трансфер игрока в другой клуб":
            transfer_player()


def transfer_player():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT club_id, name FROM Club ORDER BY name;")
    clubs = cursor.fetchall()
    club_dict = {club[1]: club[0] for club in clubs}

    st.header("Оформить трансфер игрока в другой клуб")

    or_club_name = st.selectbox("Выберите клуб, в котором игрок сейчас играет", options=list(club_dict.keys()))
    cursor.execute(
        """
        SELECT player_id, name 
        FROM Player
        WHERE club_id = %s
        ORDER BY name;
        """, (club_dict[or_club_name],))
    players = cursor.fetchall()
    player_dict = {player[1]: player[0] for player in players}

    conn.close()

    player_name = st.selectbox("Выберите игрока", options=list(player_dict.keys()))
    salary = st.number_input("Введите новую зарплату", min_value=0, max_value=999999999, step=10000, value=100000)
    tr_club_name = st.selectbox("Выберите клуб, в который игрок перейдёт", options=list(club_dict.keys()))

    if st.button("Оформить трансфер игрока"):
        if or_club_name == tr_club_name:
            st.error('Игрок не может перейти в клуб, в котором уже играет')
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE Player 
                SET club_id = %s, salary = %s
                WHERE player_id = %s
                """,
                (club_dict[tr_club_name], salary, player_dict[player_name])
            )
            conn.commit()
            st.success(f"Игрок \"{player_name}\" добавлен в клуб \"{tr_club_name}\" с зарплатой {salary}$ в год.")
        except Exception as e:
            conn.rollback()
            st.error(f"Ошибка: {e}")
        finally:
            conn.close()


def add_trophy_to_club():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT club_id, name FROM Club ORDER BY name;")
    clubs = cursor.fetchall()
    club_dict = {club[1]: club[0] for club in clubs}

    cursor.execute("SELECT trophy_id, name FROM Trophy ORDER BY name;")
    trophies = cursor.fetchall()
    trophy_dict = {trophy[1]: trophy[0] for trophy in trophies}

    conn.close()

    st.header("Добавить трофей клубу")

    club_name = st.selectbox("Выберите клуб", options=list(club_dict.keys()))
    trophy_name = st.selectbox("Выберите трофей", options=list(trophy_dict.keys()))
    year_won = st.number_input("Введите год получения трофея", min_value=1800, max_value=2100, step=1, value=2023)

    if st.button("Добавить трофей"):
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO Club_Trophy (club_id, trophy_id, year_won)
                VALUES (%s, %s, %s);
                """,
                (club_dict[club_name], trophy_dict[trophy_name], year_won)
            )
            conn.commit()
            st.success(f"Трофей \"{trophy_name}\" добавлен клубу \"{club_name}\" за {year_won} год.")
        except Exception as e:
            conn.rollback()
            st.error(f"Ошибка: {e}")
        finally:
            conn.close()


def display_club_filtering():
    cities, stadiums = get_unique_values()
    st.sidebar.header("Фильтры")
    filters = {}

    min_rating = st.sidebar.slider("Минимальный рейтинг клуба", 0, 100, 0)
    if min_rating > 0:
        filters["rating"] = min_rating

    city_filter = st.sidebar.selectbox("Город", ["Все"] + cities)
    if city_filter != "Все":
        filters["city"] = city_filter

    stadium_filter = st.sidebar.selectbox("Стадион", ["Все"] + stadiums)
    if stadium_filter != "Все":
        filters["stadium"] = stadium_filter

    if st.sidebar.button("Применить фильтры"):
        st.write("Результаты фильтрации:")
        clubs = get_filtered_clubs(filters)
        if clubs:
            st.table([{"Название клуба": club[0], "Стадион": club[1], "Город": club[2], "Рейтинг": club[3],
                       "Кол-во игроков": club[4]} for club in
                      clubs])
        else:
            st.write("Нет данных, соответствующих фильтрам.")


def display_additional_info():
    st.title("Дополнительная информация о клубах")
    st.sidebar.header("Выберите тип информации")
    query_type = st.sidebar.selectbox(
        "Что вы хотите узнать?",
        ["Список игроков клуба", "Список трофеев клуба", "Клубы, выигравшие трофей", "Клубы из страны"]
    )

    if query_type == "Список игроков клуба":
        club_name = st.selectbox("Выберете клуб из списка", get_clubs())
        if club_name:
            players = get_players_by_club(club_name)
            if st.button('Показать список'):
                st.table(
                    [{'Имя игрока': player[0], 'Позиция': player[1], 'Возраст': player[2], 'Зарплата': player[3]} for
                     player in players] if players else [{"Сообщение": "Нет игроков для этого клуба"}])
                st.table([{'Название клуба': club[0], 'Рейтинг клуба': club[1], 'Количество игроков': club[2]} for club in players_count(club_name)])

    elif query_type == "Список трофеев клуба":
        club_name = st.selectbox("Выберете клуб из списка", get_clubs())
        if club_name:
            trophies = get_trophies_by_club(club_name)
            if st.button('Показать список'):
                st.table(
                    [{'Название трофея': trophy[0], 'Год получения': trophy[1], 'Призовой фонд': trophy[2]} for trophy
                     in trophies] if trophies else [{"Сообщение": "Клуб не выиграл трофеев"}])
                st.caption(f"Количество трофеев у клуба {club_name}: {trophies_count(club_name)}")

    elif query_type == "Клубы, выигравшие трофей":
        trophy_name = st.selectbox("Выберете трофей из списка", get_trophies())
        if trophy_name:
            clubs = get_clubs_by_trophy(trophy_name)
            if st.button('Показать список'):
                st.table([{'Название клуба': club[0], 'Год получения': club[1]} for club in clubs] if clubs else [
                    {"Сообщение": "Нет клубов, выигравших этот трофей"}])
                st.caption(f"Количество клубов выигравших {trophy_name}: {trophywinners_count(trophy_name)}")

    elif query_type == "Клубы из страны":
        country_name = st.selectbox("Выберете страну из списка", get_country())
        if country_name:
            clubs = get_clubs_by_country(country_name)
            if st.button('Показать список'):
                st.table([{'Название клуба': club[0], 'Город': club[1]} for club in clubs] if clubs else [
                    {"Сообщение": "Нет клубов из этой страны"}])
                st.caption(f"Количество клубов, находящихся в стране {country_name}: {clubsincountry_count(country_name)}")
