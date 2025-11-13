import asyncpg

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
                            zone_id              VARCHAR(20),
                            stop_url             VARCHAR(200),
                           stop_desc            VARCHAR(200),
                            stop_timezone        VARCHAR(50),
                           level_id             VARCHAR(20),
                            platform_code        VARCHAR(20),
                           stop_code            VARCHAR(20),
                           location_type        INT,
                           location_sub_type    VARCHAR(100),
                           parent_station       VARCHAR(100),
                           wheelchair_boarding  INT
                           )
                       ''')
    print("Table 'users' créée ou déjà existante")
    await close_pool(conn)
