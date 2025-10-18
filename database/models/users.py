from datetime import datetime
from bson import ObjectId


class UsersTable:
    def __init__(self, db):
        self.collection = db['users']
        self._create_indexes()

    def _create_indexes(self):
        self.collection.create_index('email', unique=True)
        self.collection.create_index('username', unique=True)

    def create_user(self, user_data):
        user = {
            'username': user_data['username'],
            'email': user_data['email'],
            'password_hash': user_data['password_hash'],
            'profile': {
                'first_name': user_data.get('first_name', ''),
                'last_name': user_data.get('last_name', ''),
                'avatar_url': user_data.get('avatar_url', '')
            },
            'settings': {
                'theme': 'light',
                'language': 'ru',
                'notifications': True
            },
            'is_active': True,
            'is_verified': False,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }

        try:
            result = self.collection.insert_one(user)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Ошибка создания пользователя: {e}")
            return None

    def get_user_by_email(self, email):
        """Найти пользователя по email"""
        return self.collection.find_one({'email': email})

    def get_user_by_id(self, user_id):
        """Найти пользователя по ID"""
        return self.collection.find_one({'_id': ObjectId(user_id)})

    def get_user_by_username(self, username):
        """Найти пользователя по username"""
        return self.collection.find_one({'username': username})

    def update_user(self, user_id, update_data):
        """Обновить данные пользователя"""
        update_data['updated_at'] = datetime.utcnow()

        result = self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0

    def delete_user(self, user_id):
        """Удалить пользователя"""
        result = self.collection.delete_one({'_id': ObjectId(user_id)})
        return result.deleted_count > 0

    def search_users(self, query, limit=10):
        """Поиск пользователей по имени или email"""
        return list(self.collection.find({
            '$or': [
                {'username': {'$regex': query, '$options': 'i'}},
                {'email': {'$regex': query, '$options': 'i'}},
                {'profile.first_name': {'$regex': query, '$options': 'i'}},
                {'profile.last_name': {'$regex': query, '$options': 'i'}}
            ]
        }).limit(limit))