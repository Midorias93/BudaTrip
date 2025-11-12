from DataBase import Tables

async def fill_bkk_table(file_path: str = 'stops.txt') -> int:
    conn = await Tables.init_pool()

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            next(file)

            records = []

            for line in file:
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
            await Tables.close_pool(conn)
            return inserted_count
    except Exception as e :
        print("File does not exist", e)
        await Tables.close_pool(conn)


async def clear_bkk_table() :
    conn = await Tables.init_pool()
    await conn.execute('DELETE FROM bkk')
    await Tables.close_pool(conn)
