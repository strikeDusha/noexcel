from fastapi import *
class Row:                              #строка таблицы
    def __init__(self, number):
        self.number = number
        self.cells = {}
