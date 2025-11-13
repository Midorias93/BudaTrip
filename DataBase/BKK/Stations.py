from DataBase import Tables
import csv

async def fill_bkk_table():
    """Remplit la table bkk_stops avec les données du fichier stops.txt"""
    conn = await Tables.init_pool()

    try:
        # Vider la table avant de la remplir
        await conn.execute("TRUNCATE TABLE bkk;")

        # Lire le fichier avec le module csv qui gère les guillemets
        with open('DataBase/BKK/stops.txt', 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)

            for row in csv_reader:
                await conn.execute("""
                    INSERT INTO bkk( 
                        stop_id, stop_code, stop_name, stop_lat, stop_lon,
                        zone_id, stop_url, location_type, parent_station,
                        stop_desc, stop_timezone, wheelchair_boarding,
                        level_id, platform_code
                    ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)
                """,
                    row['stop_id'],
                    row['stop_code'] or None,
                    row['stop_name'],
                    float(row['stop_lat']) if row['stop_lat'] else None,
                    float(row['stop_lon']) if row['stop_lon'] else None,
                    row['zone_id'] or None,
                    row['stop_url'] or None,
                    int(row['location_type']) if row['location_type'] else 0,
                    row['parent_station'] or None,
                    row['stop_desc'] or None,
                    row['stop_timezone'] or None,
                    int(row['wheelchair_boarding']) if row['wheelchair_boarding'] else None,
                    row['level_id'] or None,
                    row['platform_code'] or None
                )

        print(f"Table bkk_stops remplie avec succès")

    except Exception as e:
        print(f"Erreur lors du remplissage: {e}")
        raise
    finally:
        await Tables.close_pool(conn)

async def get_all_bkk_stations():
    conn = await Tables.init_pool()
    rows = await conn.fetch('SELECT * FROM bkk')
    await Tables.close_pool(conn)
    return [dict(row) for row in rows]

async def get_bkk_station_by_stop_id(stop_id):
    conn = await Tables.init_pool()
    row = await conn.fetchrow('SELECT * FROM bkk WHERE stop_id = $1', stop_id)
    await Tables.close_pool(conn)
    return dict(row) if row else None

async def get_bkk_station_by_name(name):
    conn = await Tables.init_pool()
    row = await conn.fetchrow('SELECT * FROM bkk WHERE stop_name = $1', name)
    await Tables.close_pool(conn)
    return dict(row) if row else None

async def clear_bkk_table() :
    conn = await Tables.init_pool()
    await conn.execute('DELETE FROM bkk')
    await Tables.close_pool(conn)
