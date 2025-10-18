import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv

load_dotenv()


class Database:
    def __init__(self):
        self.client = None
        self.db = None
        self.connect()

        self.users = UsersTable(self.db)
        self.spreadsheets = SpreadsheetsTable(self.db)
        self.rows = RowsTable(self.db)

    def connect(self):
        try:
            self.client = MongoClient(
                host=os.getenv('MONGO_HOST', 'localhost'),
                port=int(os.getenv('MONGO_PORT', 27017)),
                username=os.getenv('MONGO_USERNAME'),
                password=os.getenv('MONGO_PASSWORD')
            )

            self.client.admin.command('ping')
            self.db = self.client[os.getenv('DATABASE_NAME', 'spreadsheet_app')]
            print("✅ Успешное подключение к MongoDB")

        except ConnectionFailure as e:
            print(f"❌ Ошибка подключения к MongoDB: {e}")
            raise

    def close(self):
        if self.client:
            self.client.close()