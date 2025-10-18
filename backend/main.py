from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
from typing import Union
import uuid
import pandas as pd


app = FastAPI()


database = {}


class Cell(BaseModel):
    cell_cord: str
    value: Union[int, float, str, list, None] = None
    type: Union[str, None] = None


class Raw(BaseModel):
    raw_cord: str
    cells: list[Cell] = []


class Table(BaseModel):
    name: str
    raws: list[Raw] = []


def type_defenition(value):
    try:
        val = int(value)
        type = "int"
        value = int(value)
        return {"type": type, "value": value}
    except:
        try:
            val = float(value)
            type = "float"
            value = float(value)
            return {"type": type, "value": value}
        except:
            val = bool(value)
            type = "bool"
            value = bool(value)
            return {"type": type, "value": value}
    return {"type": "str", "value": value}


@app.post("/cells/", response_model=Cell, tags=["Создать ячейку"])
def create_cell(cell: Cell):
    cell_id = str(uuid.uuid4())
    database[cell_id] = cell
    return {"value": database[cell_id], "id": cell_id}


@app.get("/cells/", tags=["Прочитать значения ячеек"])
def read_cells():
    return list(database.values())


@app.put("/cells/{cell_id}", response_model=Cell, tags=["Поменять значение в ячейке"])
def update_cell(cell_id: str, updated_cell: Cell):
    if cell_id not in database:
        raise HTTPException(status_code=404, detail="Cell not found")
    database[cell_id].update(updated_cell)
    return database[cell_id]


@app.delete("/cells/{cell_id}", tags=["Удаление ячейки"])
def delete_cell(cell_id: str):
    if cell_id not in database:
        raise HTTPException(status_code=404, detail="Cell not found")
    del database[cell_id]
    return {"detail": f"Cell with id '{cell_id}' has been deleted"}


@app.post("/uploadfile/", tags=["Загрузка Excel файла"])
async def upload_file(file: UploadFile = File(...)):
    try:
        filedata = pd.read_excel(file.file)
        output_data = []
        for index, row in filedata.iterrows():
            for column_name in filedata.columns:
                output_data.append({"row_number": index + 1, "column_name": column_name, "cell_value": row[column_name]})
        return {"result": output_data}
    except Exception as e:
        return {"error": str(e)}

