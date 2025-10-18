from datetime import datetime


class SpreadsheetsTable:
    def __init__(self, db):
        self.collection = db['spreadsheets']
        self._create_indexes()

    def _create_indexes(self):
        self.collection.create_index('owner_id')
        self.collection.create_index([('name', 1), ('owner_id', 1)])

    def create_spreadsheet(self, spreadsheet_data):
        spreadsheet = {
            'name': spreadsheet_data['name'],
            'owner_id': spreadsheet_data['owner_id'],
            'columns': ['A', 'B', 'C', 'D', 'E'],
            'metadata': {
                'default_row_count': 100,
                'frozen_columns': 0,
                'frozen_rows': 1
            },
            'shared_with': [],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'is_public': False
        }

        result = self.collection.insert_one(spreadsheet)
        return str(result.inserted_id)

    def get_user_spreadsheets(self, user_id):
        return list(self.collection.find({
            '$or': [
                {'owner_id': user_id},
                {'shared_with': user_id}
            ]
        }))

    def add_column(self, spreadsheet_id, column_name):
        from bson import ObjectId
        result = self.collection.update_one(
            {'_id': ObjectId(spreadsheet_id)},
            {
                '$addToSet': {'columns': column_name},
                '$set': {'updated_at': datetime.utcnow()}
            }
        )
        return result.modified_count > 0