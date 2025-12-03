from DataBase import Tables
import asyncpg

async def create_user(name, email, password):
    conn = await Tables.init_pool()
    try:
        row = await conn.fetchrow(
            'INSERT INTO users (name, email, password) VALUES ($1, $2, $3) RETURNING id',
            name, email, password
        )
        await Tables.close_pool(conn)
        return row['id']
    except asyncpg.UniqueViolationError:
        print(f"Error: Email {email} already exists")
        await Tables.close_pool(conn)
        return None

# ==================== READ OPERATIONS ====================

async def get_user_by_id(user_id):
    conn = await Tables.init_pool()
    row = await conn.fetchrow('SELECT * FROM users WHERE id = $1', user_id)
    await Tables.close_pool(conn)
    return dict(row) if row else None


async def get_user_by_email(email):
    conn = await Tables.init_pool()
    row = await conn.fetchrow('SELECT * FROM users WHERE email = $1', email)
    await Tables.close_pool(conn)
    return dict(row) if row else None


async def get_all_users(limit = 100, offset = 0):
    conn = await Tables.init_pool()
    rows = await conn.fetch('SELECT * FROM users LIMIT $1 OFFSET $2', limit, offset)
    await Tables.close_pool(conn)
    return [dict(row) for row in rows]


async def search_users_by_name(name):
    conn = await Tables.init_pool()
    rows = await conn.fetch(
        'SELECT * FROM users WHERE name ILIKE $1',
        f'%{name}%'
    )
    await Tables.close_pool(conn)
    return [dict(row) for row in rows]


async def count_users():
    conn = await Tables.init_pool()
    count = await conn.fetchval('SELECT COUNT(*) FROM users')
    await Tables.close_pool(conn)
    return count


async def user_exists(email):
    conn = await Tables.init_pool()
    exists = await conn.fetchval(
        'SELECT EXISTS(SELECT 1 FROM users WHERE email = $1)',
        email
    )
    await Tables.close_pool(conn)
    return exists


# ==================== UPDATE OPERATIONS ====================

async def update_user(user_id, name = None, email = None, password = None, phone = None):
    updates = []
    values = []
    param_count = 1

    if name is not None:
        updates.append(f'name = ${param_count}')
        values.append(name)
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

    conn = await Tables.init_pool()
    try:
        result = await conn.execute(query, *values)
        await Tables.close_pool(conn)
        return result.endswith('1')
    except asyncpg.UniqueViolationError:
        print(f"Error: Email {email} already exists")
        await Tables.close_pool(conn)
        return False


async def update_password(user_id, new_password):
    conn = await Tables.init_pool()
    result = await conn.execute(
        'UPDATE users SET password = $1 WHERE id = $2',
        new_password, user_id
    )
    await Tables.close_pool(conn)
    return result.endswith('1')


# ==================== OPÉRATIONS DELETE ====================

async def delete_user(user_id):
    conn = await Tables.init_pool()
    result = await conn.execute('DELETE FROM users WHERE id = $1', user_id)
    await Tables.close_pool(conn)
    return result.endswith('1')


async def delete_user_by_email(email):
    conn = await Tables.init_pool()
    result = await conn.execute('DELETE FROM users WHERE email = $1', email)
    await Tables.close_pool(conn)
    return result.endswith('1')


async def delete_all_users():
    conn = await Tables.init_pool()
    result = await conn.execute('DELETE FROM users')
    count = int(result.split()[-1]) if result else 0
    await Tables.close_pool(conn)
    return count


# ==================== TRANSACTIONS ====================

async def transfer_user_data(old_email, new_email):
    conn = await Tables.init_pool()
    async with conn.transaction():
        try:
            # Check that the old email exists
            exists = await conn.fetchval(
                'SELECT EXISTS(SELECT 1 FROM users WHERE email = $1)',
                old_email
            )
            if not exists:
                await Tables.close_pool(conn)
                return False

            # Update the email
            result = await conn.execute(
                'UPDATE users SET email = $1 WHERE email = $2',
                new_email, old_email
            )
            await Tables.close_pool(conn)
            return result.endswith('1')
        except asyncpg.UniqueViolationError:
            print(f"Error: Email {new_email} already exists")
            await Tables.close_pool(conn)
            return False
