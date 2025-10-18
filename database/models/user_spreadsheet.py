from datetime import datetime
from bson import ObjectId


class UserSpreadsheetsTable:
    def __init__(self, db):
        self.collection = db['user_spreadsheets']
        self._create_indexes()

    def _create_indexes(self):
        self.collection.create_index([('user_id', 1), ('spreadsheet_id', 1)], unique=True)
        self.collection.create_index('user_id')
        self.collection.create_index('spreadsheet_id')
        self.collection.create_index('role')

    def add_user_to_spreadsheet(self, user_id, spreadsheet_id, role='viewer'):
        if role not in ['owner', 'editor', 'viewer', 'commenter']:
            role = 'viewer'

        user_sheet = {
            'user_id': user_id,
            'spreadsheet_id': spreadsheet_id,
            'role': role,
            'permissions': self._get_permissions_for_role(role),
            'added_at': datetime.utcnow(),
            'added_by': user_id,
            'is_active': True
        }

        try:
            result = self.collection.insert_one(user_sheet)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Ошибка добавления пользователя к таблице: {e}")
            return None

    def _get_permissions_for_role(self, role):
        """Получить права доступа для роли"""
        permissions = {
            'owner': {
                'can_edit': True,
                'can_delete': True,
                'can_share': True,
                'can_comment': True,
                'can_manage_users': True
            },
            'editor': {
                'can_edit': True,
                'can_delete': False,
                'can_share': False,
                'can_comment': True,
                'can_manage_users': False
            },
            'commenter': {
                'can_edit': False,
                'can_delete': False,
                'can_share': False,
                'can_comment': True,
                'can_manage_users': False
            },
            'viewer': {
                'can_edit': False,
                'can_delete': False,
                'can_share': False,
                'can_comment': False,
                'can_manage_users': False
            }
        }
        return permissions.get(role, permissions['viewer'])

    def get_user_spreadsheets(self, user_id):
        pipeline = [
            {
                '$match': {
                    'user_id': user_id,
                    'is_active': True
                }
            },
            {
                '$lookup': {
                    'from': 'spreadsheets',
                    'localField': 'spreadsheet_id',
                    'foreignField': '_id',
                    'as': 'spreadsheet_info'
                }
            },
            {
                '$unwind': '$spreadsheet_info'
            },
            {
                '$project': {
                    'spreadsheet_id': 1,
                    'role': 1,
                    'permissions': 1,
                    'added_at': 1,
                    'name': '$spreadsheet_info.name',
                    'description': '$spreadsheet_info.description',
                    'owner_id': '$spreadsheet_info.owner_id',
                    'created_at': '$spreadsheet_info.created_at',
                    'updated_at': '$spreadsheet_info.updated_at'
                }
            }
        ]

        return list(self.collection.aggregate(pipeline))

    def get_spreadsheet_users(self, spreadsheet_id):
        pipeline = [
            {
                '$match': {
                    'spreadsheet_id': spreadsheet_id,
                    'is_active': True
                }
            },
            {
                '$lookup': {
                    'from': 'users',
                    'localField': 'user_id',
                    'foreignField': '_id',
                    'as': 'user_info'
                }
            },
            {
                '$unwind': '$user_info'
            },
            {
                '$project': {
                    'user_id': 1,
                    'role': 1,
                    'permissions': 1,
                    'added_at': 1,
                    'username': '$user_info.username',
                    'email': '$user_info.email',
                    'profile': '$user_info.profile'
                }
            }
        ]

        return list(self.collection.aggregate(pipeline))

    def update_user_role(self, spreadsheet_id, user_id, new_role):
        result = self.collection.update_one(
            {
                'spreadsheet_id': spreadsheet_id,
                'user_id': user_id
            },
            {
                '$set': {
                    'role': new_role,
                    'permissions': self._get_permissions_for_role(new_role)
                }
            }
        )
        return result.modified_count > 0

    def remove_user_from_spreadsheet(self, spreadsheet_id, user_id):
        """Удалить пользователя из таблицы"""
        result = self.collection.delete_one({
            'spreadsheet_id': spreadsheet_id,
            'user_id': user_id
        })
        return result.deleted_count > 0

    def can_user_access(self, user_id, spreadsheet_id, permission=None):
        access = self.collection.find_one({
            'user_id': user_id,
            'spreadsheet_id': spreadsheet_id,
            'is_active': True
        })

        if not access:
            return False

        if permission and permission in access.get('permissions', {}):
            return access['permissions'][permission]

        return True

    def get_user_role(self, user_id, spreadsheet_id):
        access = self.collection.find_one({
            'user_id': user_id,
            'spreadsheet_id': spreadsheet_id,
            'is_active': True
        })
        return access.get('role') if access else None