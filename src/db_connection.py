import psycopg2


def get_db_connection():
    conn = psycopg2.connect(
        dbname="football_service",
        user="postgres",
        password="Logitech1524",
        host="localhost",
        port="5432"
    )
    return conn


def get_country():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT name
        FROM country
        ORDER BY 1;
        """
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()

    return [country[0] for country in results]


def get_trophies():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
        SELECT name
        FROM trophy
        ORDER BY 1;
        """
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()

    return [trophy[0] for trophy in results]

def get_clubs():
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    SELECT name
    FROM Club
    ORDER BY 1;
    """
    cursor.execute(query)
    results = cursor.fetchall()
    conn.close()

    return [club[0] for club in results]

# Функция для получения уникальных значений для фильтров
def get_unique_values():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT DISTINCT ci.name FROM City ci ORDER BY ci.name;")
    cities = [row[0] for row in cursor.fetchall()]

    cursor.execute("SELECT DISTINCT s.name FROM Stadium s ORDER BY s.name;")
    stadiums = [row[0] for row in cursor.fetchall()]

    conn.close()
    return cities, stadiums


# Функция для получения клубов с фильтрацией
def get_filtered_clubs(filters):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT c.name, s.name AS stadium, ci.name AS city, c.rating, COUNT(player_id)
    FROM Club c
    JOIN Stadium s ON c.stadium_id = s.stadium_id
    JOIN City ci ON s.city_id = ci.city_id
    JOIN Player p ON c.club_id = p.club_id
    WHERE 1=1
    """

    params = []

    # Передача условий фильтрации из словаря
    if "rating" in filters:
        query += " AND c.rating >= %s"
        params.append(filters["rating"])

    if "city" in filters:
        query += " AND ci.name = %s"
        params.append(filters["city"])

    if "stadium" in filters:
        query += " AND s.name = %s"
        params.append(filters["stadium"])

    query += "GROUP BY 1, 2, 3, 4 ORDER BY c.rating DESC;"

    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    return results


# Получение игроков клуба
def get_players_by_club(club_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    SELECT p.name, p.position, p.age, p.salary
    FROM Player p
    JOIN Club c ON p.club_id = c.club_id
    WHERE c.name = %s
    ORDER BY 1;
    """
    cursor.execute(query, (club_name,))
    players = cursor.fetchall()
    conn.close()
    return players


# Получение трофеев, выигранных клубом
def get_trophies_by_club(club_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    SELECT t.name, ct.year_won, t.prize_fund
    FROM Club_Trophy ct
    JOIN Trophy t ON ct.trophy_id = t.trophy_id
    JOIN Club c ON ct.club_id = c.club_id
    WHERE c.name = %s
    ORDER BY 2;
    """
    cursor.execute(query, (club_name,))
    trophies = cursor.fetchall()
    conn.close()
    return trophies

# Получение клубов, выигравших определенный трофей
def get_clubs_by_trophy(trophy_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    SELECT c.name, ct.year_won
    FROM Club_Trophy ct
    JOIN Trophy t ON ct.trophy_id = t.trophy_id
    JOIN Club c ON ct.club_id = c.club_id
    WHERE t.name = %s
    ORDER BY 2;
    """
    cursor.execute(query, (trophy_name,))
    clubs = cursor.fetchall()
    conn.close()
    return clubs

# Получение клубов из определенной страны
def get_clubs_by_country(country_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = """
    SELECT c.name, ci.name
    FROM Club c
    JOIN Stadium s ON c.stadium_id = s.stadium_id
    JOIN City ci ON s.city_id = ci.city_id
    JOIN Country co ON ci.country_id = co.country_id
    WHERE co.name = %s
    ORDER BY 1;
    """
    cursor.execute(query, (country_name,))
    clubs = cursor.fetchall()
    conn.close()
    return clubs

