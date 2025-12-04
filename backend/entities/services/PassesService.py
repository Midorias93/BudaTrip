from backend.entities.models.PassesModel import Pass
from peewee import DoesNotExist


# ==================== CREATE OPERATIONS ====================

def create_pass(pass_type, price, user_id):
    """Create a new transport pass
    
    Args:
        pass_type: Required. Type of the pass (e.g., MONTHLY, WEEKLY).
        price: Required. Price of the pass.
        user_id: Required. ID of the user who owns the pass.
    
    Returns:
        Pass ID if successful, None otherwise.
    """
    if pass_type is None or price is None or user_id is None:
        print("Error: pass_type, price, and user_id are all required")
        return None
        
    try:
        transport_pass = Pass.create(
            type=pass_type,
            price=price,
            user_id=user_id
        )
        return transport_pass.id
    except Exception as e:
        print(f"Error creating pass: {e}")
        return None


# ==================== READ OPERATIONS ====================

def get_pass_by_id(pass_id):
    """Get a pass by ID"""
    try:
        transport_pass = Pass.get_by_id(pass_id)
        return {
            'id': transport_pass.id,
            'type': transport_pass.type,
            'price': transport_pass.price,
            'user_id': transport_pass.user_id.id if transport_pass.user_id else None
        }
    except DoesNotExist:
        return None


def get_all_passes(limit=100, offset=0):
    """Get all passes with pagination"""
    passes = Pass.select().limit(limit).offset(offset)
    return [
        {
            'id': p.id,
            'type': p.type,
            'price': p.price,
            'user_id': p.user_id.id if p.user_id else None
        }
        for p in passes
    ]


def get_passes_by_user(user_id, limit=100):
    """Get all passes for a specific user"""
    passes = Pass.select().where(Pass.user_id == user_id).limit(limit)
    return [
        {
            'id': p.id,
            'type': p.type,
            'price': p.price,
            'user_id': p.user_id.id if p.user_id else None
        }
        for p in passes
    ]


def get_passes_by_type(pass_type, limit=100):
    """Get all passes of a specific type"""
    passes = Pass.select().where(Pass.type == pass_type).limit(limit)
    return [
        {
            'id': p.id,
            'type': p.type,
            'price': p.price,
            'user_id': p.user_id.id if p.user_id else None
        }
        for p in passes
    ]


def count_passes():
    """Count total number of passes"""
    return Pass.select().count()


def count_passes_by_user(user_id):
    """Count passes for a specific user"""
    return Pass.select().where(Pass.user_id == user_id).count()


# ==================== UPDATE OPERATIONS ====================

def update_pass(pass_id, pass_type=None, price=None):
    """Update a pass's information"""
    try:
        transport_pass = Pass.get_by_id(pass_id)
        
        # Update only provided fields
        if pass_type is not None:
            transport_pass.type = pass_type
        if price is not None:
            transport_pass.price = price
        
        transport_pass.save()
        return True
    except DoesNotExist:
        return False


# ==================== DELETE OPERATIONS ====================

def delete_pass(pass_id):
    """Delete a pass by ID"""
    try:
        transport_pass = Pass.get_by_id(pass_id)
        transport_pass.delete_instance()
        return True
    except DoesNotExist:
        return False


def delete_passes_by_user(user_id):
    """Delete all passes for a user"""
    count = Pass.delete().where(Pass.user_id == user_id).execute()
    return count


def delete_all_passes():
    """Delete all passes"""
    count = Pass.delete().execute()
    return count
