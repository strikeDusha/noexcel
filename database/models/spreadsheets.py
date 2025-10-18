from datetime import datetime


class SpreadsheetsTable:
    def __init__(self, db):
        self.collection = db['spreadsheets']
        self._create_indexes()

    def _create_indexes(self):
        self.collection.create_index('owner_id')
        self.collection.create_index([('name', 1), ('owner_id', 1)])

    def _generate_columns(self, count=26):
        """Генерация названий колонок: A, B, C, ..., Z, AA, AB, ..."""
        columns = []
        for i in range(count):
            if i < 26:
                # Однобуквенные колонки A-Z
                columns.append(chr(65 + i))  # 65 - код 'A'
            else:
                # Двухбуквенные колонки AA, AB, ...
                first_letter = chr(65 + (i // 26) - 1)
                second_letter = chr(65 + (i % 26))
                columns.append(f"{first_letter}{second_letter}")
        return columns

    def _get_next_column_name(self, current_columns):
        """Получить следующее название колонки после последней существующей"""
        if not current_columns:
            return 'A'

        last_column = current_columns[-1]

        # Если последняя колонка однобуквенная
        if len(last_column) == 1:
            if last_column < 'Z':
                return chr(ord(last_column) + 1)
            else:
                return 'AA'

        # Если последняя колонка двухбуквенная
        if len(last_column) == 2:
            first_letter = last_column[0]
            second_letter = last_column[1]

            if second_letter < 'Z':
                return f"{first_letter}{chr(ord(second_letter) + 1)}"
            else:
                next_first = chr(ord(first_letter) + 1)
                return f"{next_first}A"

        # Для более длинных названий (если понадобится)
        return f"{last_column}_1"

    def create_spreadsheet(self, spreadsheet_data):
        """Создать новую таблицу с 26 колонками по умолчанию"""
        spreadsheet = {
            'name': spreadsheet_data['name'],
            'owner_id': spreadsheet_data['owner_id'],
            'columns': self._generate_columns(26),  # A, B, C, ..., Z
            'metadata': {
                'default_row_count': 100,
                'max_rows': 100,  # максимальное количество строк по умолчанию
                'frozen_columns': 0,
                'frozen_rows': 1,
                'next_row_index': 0  # индекс следующей новой строки
            },
            'shared_with': [],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'is_public': False
        }

        result = self.collection.insert_one(spreadsheet)
        return str(result.inserted_id)

    def get_user_spreadsheets(self, user_id):
        """Получить все таблицы пользователя"""
        return list(self.collection.find({
            '$or': [
                {'owner_id': user_id},
                {'shared_with': user_id}
            ]
        }))

    def add_column(self, spreadsheet_id):
        """Добавить новую колонку с автоматическим названием"""
        from bson import ObjectId

        # Сначала получаем текущие колонки
        spreadsheet = self.collection.find_one({'_id': ObjectId(spreadsheet_id)})
        if not spreadsheet:
            return None

        current_columns = spreadsheet.get('columns', [])
        next_column = self._get_next_column_name(current_columns)

        # Добавляем новую колонку
        result = self.collection.update_one(
            {'_id': ObjectId(spreadsheet_id)},
            {
                '$push': {'columns': next_column},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )

        return next_column if result.modified_count > 0 else None

    def add_rows(self, spreadsheet_id, count=1):
        """Добавить новые пустые строки (увеличиваем счетчик)"""
        from bson import ObjectId

        result = self.collection.update_one(
            {'_id': ObjectId(spreadsheet_id)},
            {
                '$inc': {'metadata.max_rows': count},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )

        return result.modified_count > 0

    def get_spreadsheet_info(self, spreadsheet_id):
        """Получить информацию о таблице (без строк)"""
        from bson import ObjectId
        return self.collection.find_one({'_id': ObjectId(spreadsheet_id)})

    def update_metadata(self, spreadsheet_id, metadata_updates):
        """Обновить метаданные таблицы"""
        from bson import ObjectId

        update_fields = {f'metadata.{k}': v for k, v in metadata_updates.items()}
        update_fields['updated_at'] = datetime.utcnow()

        result = self.collection.update_one(
            {'_id': ObjectId(spreadsheet_id)},
            {'$set': update_fields}
        )

        return result.modified_count > 0