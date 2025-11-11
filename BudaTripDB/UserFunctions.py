import asyncpg
from typing import Optional, List, Dict

DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'user': 'BudaTrip',
    'password': '1234',
    'database': 'BudaTripDB'
}


# ==================== GESTION DU POOL ====================

async def init_pool(min_size: int = 10, max_size: int = 20):
    pool = await asyncpg.create_pool(**DB_CONFIG, min_size=min_size, max_size=max_size)
    print("Pool de connexions initialisé")
    return pool


async def close_pool(pool):
        await pool.close()
        print("Pool de connexions fermé")


# ==================== CRÉATION DE TABLE ====================

async def create_table():
    conn = await init_pool()
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            nom VARCHAR(100),
            email VARCHAR(100) UNIQUE,
            phone VARCHAR(12) UNIQUE,
            password VARCHAR(100) NOT NULL
        )
    ''')
    await conn.execute('''
        CREATE TABLE IF NOT EXISTS bkk (
      stop_id              VARCHAR(20) PRIMARY KEY,
      stop_name            VARCHAR(100),
      stop_lat             DOUBLE PRECISION,
      stop_lon             DOUBLE PRECISION,
      stop_code            VARCHAR(20),
      location_type        VARCHAR(100),
      location_sub_type    VARCHAR(100),
      parent_station       VARCHAR(100),
      wheelchair_boarding  INT
        )
    ''')
    print("Table 'users' créée ou déjà existante")
    await close_pool(conn)


# ==================== REMPLISSAGE DE LA TABLE BKK ====================

async def fill_bkk_table(file_path: str = 'stops.txt') -> int:
    conn = await init_pool()

    try:
        # Lire le fichier
        with open(file_path, 'r', encoding='utf-8') as file:
            # Ignorer la première ligne (en-têtes)
            next(file)

            records = []

            for line in file:
                # Enlever les espaces et sauts de ligne
                line = line.strip()
                if not line:
                    continue

                parts = line.split(',')
                if len(parts) <= 9:

                    stop_id = parts[0].strip()
                    stop_name = parts[1].strip('"')
                    stop_lat = float(parts[2]) if parts[2].strip() else None
                    stop_lon = float(parts[3]) if parts[3].strip() else None
                    stop_code = parts[4] if parts[4].strip() else None
                    location_type = parts[5] if parts[5].strip() else None
                    location_sub_type = parts[6] if parts[6].strip() else None
                    parent_station = parts[7] if parts[7].strip() else None
                    wheelchair_boarding = int(parts[8]) if parts[8].strip() else None

                    records.append((
                        stop_id,
                        stop_name,
                        stop_lat,
                        stop_lon,
                        stop_code,
                        location_type,
                        location_sub_type,
                        parent_station,
                        wheelchair_boarding
                    ))

            if records:
                await conn.executemany('''
                                       INSERT INTO bkk (stop_id, stop_name, stop_lat, stop_lon, stop_code,
                                                        location_type, location_sub_type, parent_station,
                                                        wheelchair_boarding)
                                       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9) ON CONFLICT (stop_id) DO NOTHING
                                       ''', records)
            inserted_count = len(records)
            await close_pool(conn)
            return inserted_count
    except Exception as e :
        print("Le fichier n'existe pas", e)
        await close_pool(conn)


async def clear_bkk_table() :
    conn = await init_pool()
    await conn.execute('DELETE FROM bkk')
    await close_pool(conn)


# ==================== OPÉRATIONS CREATE ====================

async def create_user(nom: str, email: str, password: str) -> Optional[int]:
    conn = await init_pool()
    try:
        row = await conn.fetchrow(
            'INSERT INTO users (nom, email, password) VALUES ($1, $2, $3) RETURNING id',
            nom, email, password
        )
        await close_pool(conn)
        return row['id']
    except asyncpg.UniqueViolationError:
        print(f"Erreur : L'email {email} existe déjà")
        await close_pool(conn)
        return None

# ==================== OPÉRATIONS READ ====================

async def get_user_by_id(user_id: int) -> Optional[Dict]:
    conn = await init_pool()
    row = await conn.fetchrow('SELECT * FROM users WHERE id = $1', user_id)
    await close_pool(conn)
    return dict(row) if row else None


async def get_user_by_email(email: str) -> Optional[Dict]:
    conn = await init_pool()
    row = await conn.fetchrow('SELECT * FROM users WHERE email = $1', email)
    await close_pool(conn)
    return dict(row) if row else None


async def get_all_users(limit: int = 100, offset: int = 0) -> List[Dict]:
    conn = await init_pool()
    rows = await conn.fetch('SELECT * FROM users LIMIT $1 OFFSET $2', limit, offset)
    await close_pool(conn)
    return [dict(row) for row in rows]


async def search_users_by_name(nom: str) -> List[Dict]:
    conn = await init_pool()
    rows = await conn.fetch(
        'SELECT * FROM users WHERE nom ILIKE $1',
        f'%{nom}%'
    )
    await close_pool(conn)
    return [dict(row) for row in rows]


async def count_users() -> int:
    conn = await init_pool()
    count = await conn.fetchval('SELECT COUNT(*) FROM users')
    await close_pool(conn)
    return count


async def user_exists(email: str) -> bool:
    conn = await init_pool()
    exists = await conn.fetchval(
        'SELECT EXISTS(SELECT 1 FROM users WHERE email = $1)',
        email
    )
    await close_pool(conn)
    return exists


# ==================== OPÉRATIONS UPDATE ====================

async def update_user(user_id: int, nom: Optional[str] = None,
                      email: Optional[str] = None,
                      password: Optional[str] = None,
                        phone: Optional[int] = None ) -> bool:
    updates = []
    values = []
    param_count = 1

    if nom is not None:
        updates.append(f'nom = ${param_count}')
        values.append(nom)
        param_count += 1

    if email is not None:
        updates.append(f'email = ${param_count}')
        values.append(email)
        param_count += 1

    if password is not None:
        updates.append(f'password = ${param_count}')
        values.append(password)
        param_count += 1

    if phone is not None:
        updates.append(f'phone = ${param_count}')
        values.append(phone)
        param_count += 1

    if not updates:
        return False

    values.append(user_id)
    query = f'UPDATE users SET {", ".join(updates)} WHERE id = ${param_count}'

    conn = await init_pool()
    try:
        result = await conn.execute(query, *values)
        await close_pool(conn)
        return result.endswith('1')
    except asyncpg.UniqueViolationError:
        print(f"Erreur : L'email {email} existe déjà")
        await close_pool(conn)
        return False


async def update_password(user_id: int, new_password: str) -> bool:
    conn = await init_pool()
    result = await conn.execute(
        'UPDATE users SET password = $1 WHERE id = $2',
        new_password, user_id
    )
    await close_pool(conn)
    return result.endswith('1')


# ==================== OPÉRATIONS DELETE ====================

async def delete_user(user_id: int) -> bool:
    conn = await init_pool()
    result = await conn.execute('DELETE FROM users WHERE id = $1', user_id)
    await close_pool(conn)
    return result.endswith('1')


async def delete_user_by_email(email: str) -> bool:
    conn = await init_pool()
    result = await conn.execute('DELETE FROM users WHERE email = $1', email)
    await close_pool(conn)
    return result.endswith('1')


async def delete_all_users() -> int:
    conn = await init_pool()
    result = await conn.execute('DELETE FROM users')
    count = int(result.split()[-1]) if result else 0
    await close_pool(conn)
    return count


# ==================== TRANSACTIONS ====================

async def transfer_user_data(old_email: str, new_email: str) -> bool:
    conn = await init_pool()
    async with conn.transaction():
        try:
            # Vérifie que l'ancien email existe
            exists = await conn.fetchval(
                'SELECT EXISTS(SELECT 1 FROM users WHERE email = $1)',
                old_email
            )
            if not exists:
                await close_pool(conn)
                return False

            # Met à jour l'email
            result = await conn.execute(
                'UPDATE users SET email = $1 WHERE email = $2',
                new_email, old_email
            )
            await close_pool(conn)
            return result.endswith('1')
        except asyncpg.UniqueViolationError:
            print(f"Erreur : L'email {new_email} existe déjà")
            await close_pool(conn)
            return False