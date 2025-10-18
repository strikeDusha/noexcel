from datetime import datetime


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
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'is_active': True
        }

        try:
            result = self.collection.insert_one(user)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Ошибка создания пользователя: {e}")
            return None

    def get_user_by_email(self, email):
        return self.collection.find_one({'email': email})

    def get_user_by_id(self, user_id):
        from bson import ObjectId
        return self.collection.find_one({'_id': ObjectId(user_id)})

    def update_user(self, user_id, update_data):
        from bson import ObjectId
        update_data['updated_at'] = datetime.utcnow()

        result = self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0