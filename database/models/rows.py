from datetime import datetime


class RowsTable:
    def __init__(self, db):
        self.collection = db['rows']
        self._create_indexes()

    def _create_indexes(self):
        """Индексы для быстрого поиска строк"""
        self.collection.create_index([
            ('spreadsheet_id', 1),
            ('row_index', 1)
        ], unique=True)

    def _is_row_empty(self, cells):
        """Проверяет, является ли строка пустой"""
        if not cells:
            return True
        return all(value is None or value == '' for value in cells.values())

    def create_or_update_row(self, spreadsheet_id, row_index, cells_data, user_id):
        """Создать или обновить строку (храним только если не пустая)"""
        # Проверяем, пустая ли строка после обновления
        if self._is_row_empty(cells_data):
            # Если строка пустая - удаляем её из БД если она существует
            self.collection.delete_one({
                'spreadsheet_id': spreadsheet_id,
                'row_index': row_index
            })
            return "deleted"  # или None, в зависимости от логики
        else:
            # Строка не пустая - создаем/обновляем
            row = {
                'spreadsheet_id': spreadsheet_id,
                'row_index': row_index,
                'cells': cells_data,
                'updated_at': datetime.utcnow(),
                'updated_by': user_id
            }

            result = self.collection.replace_one(
                {
                    'spreadsheet_id': spreadsheet_id,
                    'row_index': row_index
                },
                row,
                upsert=True
            )

            return "created" if result.upserted_id else "updated"

    def update_cell_value(self, spreadsheet_id, row_index, column, value, user_id):
        """Обновить значение одной ячейки"""
        # Сначала получаем текущую строку
        current_row = self.collection.find_one({
            'spreadsheet_id': spreadsheet_id,
            'row_index': row_index
        })

        cells_data = current_row['cells'] if current_row else {}
        cells_data[column] = value

        # Используем общий метод для создания/обновления
        return self.create_or_update_row(spreadsheet_id, row_index, cells_data, user_id)

    def get_spreadsheet_rows(self, spreadsheet_id, skip=0, limit=100):
        """Получить заполненные строки таблицы"""
        return list(self.collection.find(
            {'spreadsheet_id': spreadsheet_id}
        ).sort('row_index', 1).skip(skip).limit(limit))

    def get_row(self, spreadsheet_id, row_index):
        """Получить конкретную строку (только если она существует)"""
        return self.collection.find_one({
            'spreadsheet_id': spreadsheet_id,
            'row_index': row_index
        })

    def delete_row(self, spreadsheet_id, row_index):
        """Удалить строку (просто удаляем из БД)"""
        result = self.collection.delete_one({
            'spreadsheet_id': spreadsheet_id,
            'row_index': row_index
        })
        return result.deleted_count > 0

    def get_filled_rows_count(self, spreadsheet_id):
        """Получить количество заполненных строк"""
        return self.collection.count_documents({
            'spreadsheet_id': spreadsheet_id
        })