from DataBase.models import User
from peewee import DoesNotExist, IntegrityError


# ==================== CREATE OPERATIONS ====================

def create_user(name, email, password):
    """Create a new user"""
    try:
        user = User.create(name=name, email=email, password=password)
        return user.id
    except IntegrityError:
        print(f"Error: Email {email} already exists")
        return None


# ==================== READ OPERATIONS ====================

def get_user_by_id(user_id):
    """Get a user by their ID"""
    try:
        user = User.get_by_id(user_id)
        return {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'password': user.password
        }
    except DoesNotExist:
        return None


def get_user_by_email(email):
    """Get a user by their email"""
    try:
        user = User.get(User.email == email)
        return {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'password': user.password
        }
    except DoesNotExist:
        return None


def get_all_users(limit=100, offset=0):
    """Get all users with pagination"""
    users = User.select().limit(limit).offset(offset)
    return [
        {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'password': user.password
        }
        for user in users
    ]


def search_users_by_name(name):
    """Search users by name (case insensitive)"""
    users = User.select().where(User.name ** f'%{name}%')
    return [
        {
            'id': user.id,
            'name': user.name,
            'email': user.email,
            'phone': user.phone,
            'password': user.password
        }
        for user in users
    ]


def count_users():
    """Count total number of users"""
    return User.select().count()


def user_exists(email):
    """Check if a user with the given email exists"""
    return User.select().where(User.email == email).exists()


# ==================== UPDATE OPERATIONS ====================

def update_user(user_id, name=None, email=None, password=None, phone=None):
    """Update a user's information"""
    try:
        user = User.get_by_id(user_id)
        
        # Update only provided fields
        if name is not None:
            user.name = name
        if email is not None:
            user.email = email
        if password is not None:
            user.password = password
        if phone is not None:
            user.phone = phone
        
        user.save()
        return True
    except DoesNotExist:
        return False
    except IntegrityError:
        print(f"Error: Email {email} already exists")
        return False


def update_password(user_id, new_password):
    """Update only the user's password"""
    try:
        user = User.get_by_id(user_id)
        user.password = new_password
        user.save()
        return True
    except DoesNotExist:
        return False


# ==================== DELETE OPERATIONS ====================

def delete_user(user_id):
    """Delete a user by ID"""
    try:
        user = User.get_by_id(user_id)
        user.delete_instance()
        return True
    except DoesNotExist:
        return False


def delete_user_by_email(email):
    """Delete a user by email"""
    try:
        user = User.get(User.email == email)
        user.delete_instance()
        return True
    except DoesNotExist:
        return False


def delete_all_users():
    """Delete all users"""
    count = User.delete().execute()
    return count


# ==================== TRANSACTIONS ====================

def transfer_user_data(old_email, new_email):
    """Transfer user data from old email to new email"""
    try:
        user = User.get(User.email == old_email)
        user.email = new_email
        user.save()
        return True
    except DoesNotExist:
        return False
    except IntegrityError:
        print(f"Error: Email {new_email} already exists")
        return False
