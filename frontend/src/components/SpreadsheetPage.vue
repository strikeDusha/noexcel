<template>
  <div class="spreadsheet-page">
    <div class="grid-wrapper">
      <table class="spreadsheet">
        <thead>
          <tr>
            <th></th>
            <th v-for="(col, colIndex) in columns" :key="colIndex">{{ col }}</th>
            <th class="add-col-cell">
              <button @click="addColumns()">Добавьте</button>
            </th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(row, rowIndex) in rows" :key="rowIndex">
            <th>{{ rowIndex + 1 }}</th>
            <td v-for="(col, colIndex) in columns" :key="colIndex">
              <div 
                class="cell-wrapper" 
                :class="{ selected: selectedCell.row === rowIndex && selectedCell.col === colIndex }"
                @click="selectCell(rowIndex, colIndex)"
              >
                <input type="text" v-model="data[rowIndex][colIndex]" />
                <div 
                  v-if="selectedCell.row === rowIndex && selectedCell.col === colIndex"
                  class="drag-handle"
                  @mousedown.stop.prevent="startDrag(rowIndex, colIndex)"
                ></div>
              </div>
            </td>
            <th v-if="rowIndex === 0" class="add-col-cell"></th>
          </tr>
          <tr>
            <th class="add-row-cell">
              <button @click="addRows()">Добавьте</button>
            </th>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";

const numInitialRows = 100;
const numInitialCols = 100;

// массив строк
const rows = ref(Array.from({ length: numInitialRows }));
const columns = ref(Array.from({ length: numInitialCols }, (_, i) => getColumnName(i)));

// данные
const data = reactive(
  Array.from({ length: numInitialRows }, () =>
    Array.from({ length: numInitialCols }, () => "")
  )
);

// выделенная ячейка
const selectedCell = reactive({ row: null, col: null });

// функции
function getColumnName(index) {
  let name = "";
  index++; // начинаем с 1
  while (index > 0) {
    const rem = (index - 1) % 26;
    name = String.fromCharCode(65 + rem) + name;
    index = Math.floor((index - 1) / 26);
  }
  return name;
}

function selectCell(row, col) {
  selectedCell.row = row;
  selectedCell.col = col;
}

function startDrag(row, col) {
  console.log("Начато взаимодействие с кружком:", row, col);
  // здесь можно потом добавить логику выделения строк/столбцов
}

function addRows() {
  rows.value.push({});
  data.push(Array(columns.value.length).fill(""));
}

function addColumns() {
  const newIndex = columns.value.length;
  columns.value.push(getColumnName(newIndex));
  data.forEach(row => row.push(""));
}
</script>

<style>
.spreadsheet-page {
  font-family: "Segoe UI", sans-serif;
  background-color: white;
  padding: 20px;
  height: 100vh;
  box-sizing: border-box;
  overflow: auto;
}

.grid-wrapper {
  overflow: auto;
  max-height: 80vh;
}

.spreadsheet {
  border-collapse: collapse;
  width: max-content;
  min-width: 100%;
}

.spreadsheet th,
.spreadsheet td {
  border: 1px solid #999;
  padding: 0;
  position: relative;
}

.spreadsheet th {
  background-color: #f0f0f0;
  position: sticky;
  top: 0;
  z-index: 2;
  text-align: center;
  min-width: 50px;
}

.spreadsheet th:first-child {
  left: 0;
  position: sticky;
  z-index: 3;
  background-color: #e0e0e0;
}

.spreadsheet td {
  width: 80px;
  height: 28px;
  padding: 0;
}

.cell-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
}

.cell-wrapper input {
  width: 100%;
  height: 100%;
  border: none;
  outline: none;
  padding: 4px;
  box-sizing: border-box;
  font-size: 0.9em;
}

.cell-wrapper.selected {
  border: 2px solid #4caf50; /* зелёная рамка */
}

.drag-handle {
  width: 8px;
  height: 8px;
  background-color: #4caf50;
  border-radius: 50%;
  position: absolute;
  bottom: 2px;
  right: 2px;
  cursor: pointer;
}

.add-col-cell button,
.add-row-cell button {
  width: 100%;
  padding: 4px;
  font-size: 0.9em;
  cursor: pointer;
}

.add-col-cell button {
  height: 28px;
}

.add-row-cell button {
  height: 28px;
  min-width: 50px;
}
</style>
