from datetime import datetime


class RowsTable:
    def __init__(self, db):
        self.collection = db['rows']
        self._create_indexes()

    def _create_indexes(self):
        """Индексы для быстрого поиска строк по таблице и порядку"""
        self.collection.create_index([
            ('spreadsheet_id', 1),
            ('row_index', 1)
        ], unique=True)

    def create_row(self, row_data):
        """Создать новую строку"""
        row = {
            'spreadsheet_id': row_data['spreadsheet_id'],
            'row_index': row_data['row_index'],
            'cells': row_data.get('cells', {}),  # {"A": "value1", "B": "value2"}
            'style': row_data.get('style', {}),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'updated_by': row_data.get('user_id')
        }

        try:
            result = self.collection.insert_one(row)
            return str(result.inserted_id)
        except Exception as e:
            print(f"Ошибка создания строки: {e}")
            return None

    def update_row(self, spreadsheet_id, row_index, update_data):
        """Обновить строку (полностью или частично)"""
        # Если обновляем ячейки, то мержим с существующими
        if 'cells' in update_data:
            update_data = {
                '$set': {
                    **{f'cells.{k}': v for k, v in update_data['cells'].items()},
                    'updated_at': datetime.utcnow(),
                    'updated_by': update_data.get('user_id')
                }
            }
        else:
            update_data = {
                '$set': {
                    **update_data,
                    'updated_at': datetime.utcnow()
                }
            }

        result = self.collection.update_one(
            {
                'spreadsheet_id': spreadsheet_id,
                'row_index': row_index
            },
            update_data,
            upsert=True  # создаст если не существует
        )
        return result.modified_count > 0 or result.upserted_id is not None

    def update_cell_value(self, spreadsheet_id, row_index, column, value, user_id):
        """Обновить значение одной ячейки в строке"""
        result = self.collection.update_one(
            {
                'spreadsheet_id': spreadsheet_id,
                'row_index': row_index
            },
            {
                '$set': {
                    f'cells.{column}': value,
                    'updated_at': datetime.utcnow(),
                    'updated_by': user_id
                }
            },
            upsert=True  # создаст строку если её нет
        )
        return True

    def get_spreadsheet_rows(self, spreadsheet_id, skip=0, limit=100):
        """Получить строки таблицы с пагинацией"""
        return list(self.collection.find(
            {'spreadsheet_id': spreadsheet_id}
        ).sort('row_index', 1).skip(skip).limit(limit))

    def get_row(self, spreadsheet_id, row_index):
        """Получить конкретную строку"""
        return self.collection.find_one({
            'spreadsheet_id': spreadsheet_id,
            'row_index': row_index
        })

    def delete_row(self, spreadsheet_id, row_index):
        """Удалить строку"""
        result = self.collection.delete_one({
            'spreadsheet_id': spreadsheet_id,
            'row_index': row_index
        })
        return result.deleted_count > 0

    def insert_row(self, spreadsheet_id, row_index, user_id):
        """Вставить новую строку (сдвинуть существующие вниз)"""
        # Сдвигаем все строки ниже вниз
        self.collection.update_many(
            {
                'spreadsheet_id': spreadsheet_id,
                'row_index': {'$gte': row_index}
            },
            {'$inc': {'row_index': 1}}
        )

        # Создаем новую пустую строку
        return self.create_row({
            'spreadsheet_id': spreadsheet_id,
            'row_index': row_index,
            'cells': {},
            'user_id': user_id
        })