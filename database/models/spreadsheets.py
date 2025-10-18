from datetime import datetime
from bson import ObjectId


class SpreadsheetsTable:
    def __init__(self, db):
        self.collection = db['spreadsheets']
        self._create_indexes()

    def _create_indexes(self):
        """Создание индексов для таблиц"""
        self.collection.create_index('owner_id')
        self.collection.create_index([('name', 1), ('owner_id', 1)])
        self.collection.create_index('created_at')

    def _generate_columns(self, count=26):
        """Генерация названий колонок: A, B, C, ..., Z, AA, AB, ..."""
        columns = []
        for i in range(count):
            if i < 26:
                columns.append(chr(65 + i))
            else:
                first_letter = chr(65 + (i // 26) - 1)
                second_letter = chr(65 + (i % 26))
                columns.append(f"{first_letter}{second_letter}")
        return columns

    def _get_next_column_name(self, current_columns):
        """Получить следующее название колонки"""
        if not current_columns:
            return 'A'

        last_column = current_columns[-1]

        if len(last_column) == 1:
            if last_column < 'Z':
                return chr(ord(last_column) + 1)
            else:
                return 'AA'

        if len(last_column) == 2:
            first_letter = last_column[0]
            second_letter = last_column[1]

            if second_letter < 'Z':
                return f"{first_letter}{chr(ord(second_letter) + 1)}"
            else:
                next_first = chr(ord(first_letter) + 1)
                return f"{next_first}A"

        return f"{last_column}_1"

    def create_spreadsheet(self, spreadsheet_data):
        """Создать новую таблицу"""
        spreadsheet = {
            'name': spreadsheet_data['name'],
            'owner_id': spreadsheet_data['owner_id'],  # ID создателя
            'description': spreadsheet_data.get('description', ''),
            'columns': self._generate_columns(26),
            'metadata': {
                'default_row_count': 100,
                'max_rows': 100,
                'frozen_columns': 0,
                'frozen_rows': 1,
                'version': 1
            },
            'settings': {
                'is_public': False,
                'allow_comments': True,
                'allow_editing': True
            },
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'last_modified_by': spreadsheet_data['owner_id']
        }

        result = self.collection.insert_one(spreadsheet)
        return str(result.inserted_id)

    def get_spreadsheet_by_id(self, spreadsheet_id):
        """Получить таблицу по ID"""
        return self.collection.find_one({'_id': ObjectId(spreadsheet_id)})

    def update_spreadsheet(self, spreadsheet_id, update_data):
        """Обновить таблицу"""
        update_data['updated_at'] = datetime.utcnow()

        result = self.collection.update_one(
            {'_id': ObjectId(spreadsheet_id)},
            {'$set': update_data}
        )
        return result.modified_count > 0

    def add_column(self, spreadsheet_id):
        """Добавить новую колонку"""
        spreadsheet = self.collection.find_one({'_id': ObjectId(spreadsheet_id)})
        if not spreadsheet:
            return None

        current_columns = spreadsheet.get('columns', [])
        next_column = self._get_next_column_name(current_columns)

        result = self.collection.update_one(
            {'_id': ObjectId(spreadsheet_id)},
            {
                '$push': {'columns': next_column},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )

        return next_column if result.modified_count > 0 else None

    def delete_spreadsheet(self, spreadsheet_id):
        """Удалить таблицу"""
        result = self.collection.delete_one({'_id': ObjectId(spreadsheet_id)})
        return result.deleted_count > 0