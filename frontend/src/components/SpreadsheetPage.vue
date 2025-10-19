<template>
  <div class="spreadsheet-container">
    <!-- Верхняя шапка (пока пустая, можно будет добавить кнопки) -->
    <div class="spreadsheet-header"></div>

    <div class="table-wrapper" @mouseup="stopSelecting">
      <table class="spreadsheet">
        <thead>
          <tr>
            <th></th>
            <th v-for="(col, cIndex) in columns" :key="cIndex">{{ col }}</th>
            <th class="control-cell">
              <input
                v-model.number="addColsCount"
                type="number"
                min="1"
                class="small-input"
              />
              <button @click="addColumns">+ Столбцы</button>
            </th>
          </tr>
        </thead>

        <tbody>
          <tr v-for="(row, rIndex) in rows" :key="rIndex">
            <th>{{ rIndex + 1 }}</th>
            <td
              v-for="(col, cIndex) in columns"
              :key="cIndex"
              class="cell"
              :class="{ selected: isSelected(rIndex, cIndex) }"
              @mousedown="startSelecting(rIndex, cIndex)"
              @mouseover="extendSelection(rIndex, cIndex)"
              @click="selectCell(rIndex, cIndex)"
            >
              <input
                type="text"
                v-model="data[rIndex][cIndex]"
                @keydown.enter.prevent="exitEdit"
                dir="ltr"
              />
            </td>

            <th v-if="rIndex === 0" class="control-cell">
              <input
                v-model.number="addRowsCount"
                type="number"
                min="1"
                class="small-input"
              />
              <button @click="addRows">+ Строки</button>
            </th>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";

/* === Настройки по умолчанию === */
const DEFAULT_ROWS = 100;
const DEFAULT_COLS = 26; // A-Z
const MAX_ROWS = 5000;
const MAX_COLS = 300;

const rows = ref(Array.from({ length: DEFAULT_ROWS }, (_, i) => i + 1));
const columns = ref(Array.from({ length: DEFAULT_COLS }, (_, i) => getColumnName(i)));
const data = reactive(
  Array.from({ length: DEFAULT_ROWS }, () => Array.from({ length: DEFAULT_COLS }, () => ""))
);

const addRowsCount = ref(100);
const addColsCount = ref(5);

/* === Выделение === */
const selected = reactive({
  startRow: null,
  startCol: null,
  endRow: null,
  endCol: null,
  selecting: false,
});

/* === Функции === */
function getColumnName(index) {
  let name = "";
  index++;
  while (index > 0) {
    const rem = (index - 1) % 26;
    name = String.fromCharCode(65 + rem) + name;
    index = Math.floor((index - 1) / 26);
  }
  return name;
}

function addRows() {
  const toAdd = Math.min(addRowsCount.value, MAX_ROWS - rows.value.length);
  if (toAdd <= 0) return;
  for (let i = 0; i < toAdd; i++) {
    rows.value.push(rows.value.length + 1);
    data.push(Array(columns.value.length).fill(""));
  }
}

function addColumns() {
  const toAdd = Math.min(addColsCount.value, MAX_COLS - columns.value.length);
  if (toAdd <= 0) return;
  const start = columns.value.length;
  for (let i = 0; i < toAdd; i++) {
    columns.value.push(getColumnName(start + i));
    data.forEach((row) => row.push(""));
  }
}

/* === Выделение мышью === */
function startSelecting(r, c) {
  selected.startRow = r;
  selected.startCol = c;
  selected.endRow = r;
  selected.endCol = c;
  selected.selecting = true;
}

function extendSelection(r, c) {
  if (!selected.selecting) return;
  selected.endRow = r;
  selected.endCol = c;
}

function stopSelecting() {
  selected.selecting = false;
}

function isSelected(r, c) {
  if (selected.startRow === null) return false;
  const rowMin = Math.min(selected.startRow, selected.endRow);
  const rowMax = Math.max(selected.startRow, selected.endRow);
  const colMin = Math.min(selected.startCol, selected.endCol);
  const colMax = Math.max(selected.startCol, selected.endCol);
  return r >= rowMin && r <= rowMax && c >= colMin && c <= colMax;
}

function selectCell(r, c) {
  selected.startRow = r;
  selected.startCol = c;
  selected.endRow = r;
  selected.endCol = c;
}

/* === Выход из режима редактирования === */
function exitEdit(e) {
  e.target.blur();
}
</script>

<style scoped>
.spreadsheet-container {
  padding: 15px;
  height: 100vh;
  display: flex;
  flex-direction: column;
  background: white;
}

.spreadsheet-header {
  height: 50px;
  background: #f7f7f7;
  border-bottom: 1px solid #ddd;
  margin-bottom: 10px;
}

.table-wrapper {
  overflow: auto;
  flex: 1;
}

.spreadsheet {
  border-collapse: collapse;
  width: max-content;
  min-width: 100%;
  font-family: "Segoe UI", sans-serif;
}

.spreadsheet th,
.spreadsheet td {
  border: 1px solid #e0e0e0; /* легкая серая сетка */
  min-width: 80px;
  height: 26px;
  text-align: left;
  padding: 0;
  position: relative;
}

.spreadsheet th {
  background-color: #f4f4f4;
  position: sticky;
  top: 0;
  z-index: 2;
}

.spreadsheet th:first-child {
  left: 0;
  position: sticky;
  z-index: 3;
  background-color: #f4f4f4;
}

.cell input {
  width: 100%;
  height: 100%;
  border: none;
  outline: none;
  font-size: 0.9em;
  padding: 4px;
  direction: ltr; /* <-- фикс бага с RTL вводом */
  text-align: left;
  background: transparent;
  cursor: text;
}

.cell.selected {
  background-color: rgba(0, 200, 255, 0.1);
  outline: 2px solid #4caf50;
}

.small-input {
  width: 50px;
  text-align: center;
  margin-right: 4px;
  border-radius: 4px;
  border: 1px solid #ccc;
}

.control-cell {
  background: #fafafa;
  text-align: center;
  position: sticky;
  right: 0;
  z-index: 4;
}
</style>
