<template>
  <div class="spreadsheet-page" :class="{ 'view-only': ACCESS_MODE === 'view' }">
    <!-- HEADER (пустой для MVP) -->
    <div class="spreadsheet-header" ref="headerRef">
      <!-- TODO: сюда later добавить toolbar (фильтры/сорт/создание таблицы) -->
    </div>

    <!-- TABLE WRAPPER -->
    <div class="grid-wrapper" ref="gridWrapper" @scroll="onScroll">
      <table class="spreadsheet" ref="tableRef">
        <thead>
          <tr>
            <th class="corner-cell"></th>

            <!-- column headers with resizer -->
            <th
              v-for="(col, colIndex) in columns"
              :key="colIndex"
              class="col-header"
              :style="{ width: colWidths[colIndex] + 'px' }"
              @mousemove="maybeShowColResize($event, colIndex)"
              @mouseleave="hideColResizeHint(colIndex)"
            >
              <div class="col-inner">{{ col }}</div>

              <!-- column resizer handle (right edge) -->
              <div
                class="col-resizer"
                @mousedown.prevent="startColResize($event, colIndex)"
                title="Изменить ширину столбца"
              ></div>
            </th>

            <th class="add-col-cell sticky-right">
              <div class="add-controls">
                <input type="number" v-model.number="colsToAdd" min="1" :max="MAX_COLS" />
                <button @click="addColumns(colsToAdd)">+ столбцов</button>
              </div>
            </th>
          </tr>
        </thead>

        <tbody ref="tbody">
          <tr v-for="(row, rowIndex) in rows" :key="rowIndex">
            <!-- row header with resizer -->
            <th
              class="row-header"
              :style="{ height: rowHeights[rowIndex] + 'px' }"
              @mousemove="maybeShowRowResize($event, rowIndex)"
              @mouseleave="hideRowResizeHint(rowIndex)"
            >
              <div class="row-inner">{{ rowIndex + 1 }}</div>
              <div class="row-resizer" @mousedown.prevent="startRowResize($event, rowIndex)"></div>
            </th>

            <!-- cells -->
            <td
              v-for="(col, colIndex) in columns"
              :key="colIndex"
              :data-row="rowIndex"
              :data-col="colIndex"
              :class="cellClass(rowIndex, colIndex)"
              @mousedown="cellMouseDown($event, rowIndex, colIndex)"
              @click="cellClick(rowIndex, colIndex, $event)"
              @dblclick="enterEdit(rowIndex, colIndex)"
              :style="{ width: colWidths[colIndex] + 'px', height: rowHeights[rowIndex] + 'px' }"
            >
              <!-- disable inputs in view-only mode -->
              <input
                v-if="ACCESS_MODE === 'edit'"
                :data-row="rowIndex"
                :data-col="colIndex"
                type="text"
                v-model="data[rowIndex][colIndex]"
                @keydown="handleKeyNavigation($event, rowIndex, colIndex)"
                @focus="onInputFocus(rowIndex, colIndex)"
                @blur="onInputBlur(rowIndex, colIndex)"
                :style="{ cursor: selectionActiveAt(rowIndex, colIndex) ? 'text' : 'default' }"
              />

              <!-- in view mode show plain text (faster, no inputs) -->
              <div v-else class="cell-view">{{ data[rowIndex][colIndex] }}</div>

              <!-- drag-handle for fill (shows on bottom-right of selection) -->
              <div
                v-if="isSelectionActiveAt(rowIndex, colIndex)"
                class="drag-handle"
                @mousedown.stop.prevent="dragHandleMouseDown($event, rowIndex, colIndex)"
              ></div>
            </td>
          </tr>

          <!-- add rows controls sticky bottom-left -->
          <tr>
            <th class="add-row-cell sticky-bottom-left">
              <div class="add-controls">
                <input type="number" v-model.number="rowsToAdd" min="1" :max="MAX_ROWS" />
                <button @click="addRows(rowsToAdd)">+ строк</button>
              </div>
            </th>
            <td :colspan="columns.length + 1" class="sticky-bottom"></td>
          </tr>
        </tbody>
      </table>

      <!-- overlay for selection -->
      <div
        v-show="overlay.visible"
        class="selection-overlay"
        :style="{
          top: overlay.top + 'px',
          left: overlay.left + 'px',
          width: overlay.width + 'px',
          height: overlay.height + 'px'
        }"
      ></div>
    </div>
  </div>
</template>

<script setup>
/* ===== IMPORTS ===== */
import { ref, reactive, onMounted, onUnmounted, nextTick } from 'vue'

/* ===== CONSTANTS / LIMITS ===== */
const MAX_ROWS = 5000
const MAX_COLS = 300

/* ===== ACCESS MODE (comment/uncomment usage where needed) =====
   // COMMENT: переключение режима доступа к таблице
   // возможные значения: 'view' | 'edit'
   // В реальном приложении значение берётся от бэкенда/контекста пользователя.
*/
const ACCESS_MODE = ref('edit') // <-- переключи на 'view' для просмотра без редактирования

/* ===== INITIALS ===== */
const INITIAL_ROWS = 100
const INITIAL_COLS = 26

const rows = ref(Array.from({ length: INITIAL_ROWS })) // только длина важна
const columns = ref(Array.from({ length: INITIAL_COLS }, (_, i) => getColumnName(i)))

// data is reactive 2D array
const data = reactive(
  Array.from({ length: INITIAL_ROWS }, () =>
    Array.from({ length: INITIAL_COLS }, () => '')
  )
)

/* sizes: arrays of widths/heights for columns/rows (allow resizing) */
const colWidths = reactive(Array.from({ length: INITIAL_COLS }, () => 90))
const rowHeights = reactive(Array.from({ length: INITIAL_ROWS }, () => 28))

/* controls for adding */
const rowsToAdd = ref(100)
const colsToAdd = ref(5)

/* selection state (rectangle) */
const selection = reactive({
  startRow: null,
  startCol: null,
  endRow: null,
  endCol: null,
  active: false,
  editing: false
})

/* overlay for visible selection */
const overlay = reactive({ visible: false, top: 0, left: 0, width: 0, height: 0 })

/* internal flags for dragging/resizing */
let isDragging = false
let isHandleDragging = false
let isColResizing = false
let isRowResizing = false
let resizeInfo = null // { type: 'col'|'row', index, startX/startY, startSize }

/* optimization: cache cell sizes and header offsets */
const gridWrapper = ref(null)
const tableRef = ref(null)
const tbody = ref(null)
const headerRef = ref(null)

let cellWidthDefault = 90
let cellHeightDefault = 28
let headerHeight = 0
let leftStickyWidth = 50

/* requestAnimationFrame throttle flag */
let rafPending = false

/* pending changes batching for server sync */
const pendingChanges = new Map()
let batchInterval = null
const BATCH_INTERVAL = 2000 // ms

/* WebSocket connection (to backend) */
let ws = null
const WS_URL = 'ws://localhost:8000/ws' // example, see backend patch below

/* ===== HELPERS ===== */
function getColumnName(index) {
  let name = ''
  index++
  while (index > 0) {
    const rem = (index - 1) % 26
    name = String.fromCharCode(65 + rem) + name
    index = Math.floor((index - 1) / 26)
  }
  return name
}

/* clamp utility */
function clamp(v, a, b) {
  return Math.max(a, Math.min(b, v))
}

/* ===== PERFORMANCE: compute cell index from mouse position (no elementFromPoint on each mousemove) =====
   - we know header height, left sticky width, cell default sizes (or column-specific sizes)
   - compute x,y relative to wrapper + scroll, then map to indices
*/
function computeCellFromPoint(clientX, clientY) {
  const wrapper = gridWrapper.value
  if (!wrapper) return null
  const rect = wrapper.getBoundingClientRect()
  const x = clientX - rect.left + wrapper.scrollLeft
  const y = clientY - rect.top + wrapper.scrollTop

  // ignore header area
  if (y < headerHeight) return null

  // compute column index by summing widths till x crosses
  let xRem = x - leftStickyWidth // skip row headers
  if (xRem < 0) return { row: null, col: null }

  let colIndex = 0
  let accumX = 0
  for (let i = 0; i < colWidths.length; i++) {
    accumX += colWidths[i]
    if (xRem < accumX) {
      colIndex = i
      break
    }
    // if at end
    if (i === colWidths.length - 1 && xRem >= accumX) colIndex = i
  }

  // compute row index
  let yRem = y - headerHeight
  let rowIndex = 0
  let accumY = 0
  for (let r = 0; r < rowHeights.length; r++) {
    accumY += rowHeights[r]
    if (yRem < accumY) {
      rowIndex = r
      break
    }
    if (r === rowHeights.length - 1 && yRem >= accumY) rowIndex = r
  }

  if (isNaN(colIndex) || isNaN(rowIndex)) return null
  return { row: rowIndex, col: colIndex }
}

/* ===== SELECTION (optimized with rAF) ===== */
function onPointerMove(e) {
  // if resizing, handle in resize handler
  if (isColResizing || isRowResizing) return

  if (!isDragging && !isHandleDragging) return

  // throttle updates via rAF
  if (rafPending) return
  rafPending = true
  requestAnimationFrame(() => {
    const cell = computeCellFromPoint(e.clientX, e.clientY)
    if (cell && cell.row !== null && cell.col !== null) {
      selection.endRow = clamp(cell.row, 0, rows.value.length - 1)
      selection.endCol = clamp(cell.col, 0, columns.value.length - 1)
      updateOverlay()
    }
    rafPending = false
  })
}

/* start selection on mousedown */
function cellMouseDown(e, r, c) {
  // allow text focus if clicking input directly; but for selection start if clicked on cell area
  if (e.target && e.target.tagName === 'INPUT') return
  // disallow edits in view-only
  if (ACCESS_MODE.value === 'view') return

  isDragging = true
  selection.startRow = r
  selection.startCol = c
  selection.endRow = r
  selection.endCol = c
  selection.active = true
  updateOverlay()
}

/* click */
function cellClick(r, c, event) {
  // disallow edits in view-only
  if (ACCESS_MODE.value === 'view') {
    selection.startRow = r
    selection.startCol = c
    selection.endRow = r
    selection.endCol = c
    selection.active = true
    updateOverlay()
    return
  }
  // select single or expand with Shift
  if (event.shiftKey && selection.active) {
    selection.endRow = r
    selection.endCol = c
  } else {
    selection.startRow = r
    selection.startCol = c
    selection.endRow = r
    selection.endCol = c
    selection.active = true
  }
  updateOverlay()
  focusCellInput(r, c)
}

/* dblclick => focus for edit */
function enterEdit(r, c) {
  if (ACCESS_MODE.value === 'view') return
  selection.startRow = r
  selection.startCol = c
  selection.endRow = r
  selection.endCol = c
  selection.active = true
  nextTick(() => focusCellInput(r, c))
}

/* focus input */
function focusCellInput(r, c) {
  nextTick(() => {
    const selector = `input[data-row="${r}"][data-col="${c}"]`
    const el = document.querySelector(selector)
    if (el) el.focus()
  })
}

/* used by input keydown */
function handleKeyNavigation(e, r, c) {
  // allow typing normally; intercept only specific navigation keys
  const key = e.key
  const maxRow = rows.value.length - 1
  const maxCol = columns.value.length - 1

  if (key === 'Enter') {
    e.preventDefault()
    e.target.blur()
    return
  }

  if (key.startsWith('Arrow')) {
    e.preventDefault()
    if (key === 'ArrowUp' && r > 0) selectAndFocus(r - 1, c)
    if (key === 'ArrowDown' && r < maxRow) selectAndFocus(r + 1, c)
    if (key === 'ArrowLeft' && c > 0) selectAndFocus(r, c - 1)
    if (key === 'ArrowRight' && c < maxCol) selectAndFocus(r, c + 1)
  }
}

function selectAndFocus(r, c) {
  selection.startRow = r
  selection.startCol = c
  selection.endRow = r
  selection.endCol = c
  selection.active = true
  updateOverlay()
  nextTick(() => focusCellInput(r, c))
}

/* selection helpers */
function isCellSelected(r, c) {
  if (!selection.active) return false
  const r1 = Math.min(selection.startRow, selection.endRow)
  const r2 = Math.max(selection.startRow, selection.endRow)
  const c1 = Math.min(selection.startCol, selection.endCol)
  const c2 = Math.max(selection.startCol, selection.endCol)
  return r >= r1 && r <= r2 && c >= c1 && c <= c2
}
function isSelectionActiveAt(r, c) {
  if (!selection.active) return false
  return r === Math.max(selection.startRow, selection.endRow) && c === Math.max(selection.startCol, selection.endCol)
}
function selectionActiveAt(r, c) {
  return isSelectionActiveAt(r, c)
}
function cellClass(r, c) {
  const classes = []
  if (isCellSelected(r, c)) classes.push('cell-selected')
  if (isSelectionActiveAt(r, c)) classes.push('cell-handle-visible')
  return classes.join(' ')
}

/* overlay update (compute bounding box faster using cell sizes) */
function updateOverlay() {
  if (!selection.active || selection.startRow === null) {
    overlay.visible = false
    return
  }

  const r1 = Math.min(selection.startRow, selection.endRow)
  const r2 = Math.max(selection.startRow, selection.endRow)
  const c1 = Math.min(selection.startCol, selection.endCol)
  const c2 = Math.max(selection.startCol, selection.endCol)

  // compute left: sum of colWidths[0..c1-1] + leftStickyWidth - scrollLeft
  const wrapper = gridWrapper.value
  if (!wrapper) return
  const scrollLeft = wrapper.scrollLeft
  const scrollTop = wrapper.scrollTop

  const left = leftStickyWidth + sumArray(colWidths, 0, c1) - scrollLeft
  const top = headerHeight + sumArray(rowHeights, 0, r1) - scrollTop
  const width = sumArray(colWidths, c1, c2 + 1)
  const height = sumArray(rowHeights, r1, r2 + 1)

  overlay.left = left
  overlay.top = top
  overlay.width = Math.max(2, width)
  overlay.height = Math.max(2, height)
  overlay.visible = true
}

/* sum helper */
function sumArray(arr, from, to) {
  // sum arr[from] + ... + arr[to-1]
  let s = 0
  for (let i = from; i < to && i < arr.length; i++) s += arr[i]
  return s
}

/* mouse up/down hooks (global) */
function onDocMouseUp(e) {
  if (isColResizing || isRowResizing) {
    isColResizing = false
    isRowResizing = false
    resizeInfo = null
    document.removeEventListener('mousemove', onDocMouseMove)
    document.removeEventListener('mouseup', onDocMouseUp)
    return
  }

  if (isDragging || isHandleDragging) {
    // if handle drag -> fill values
    if (isHandleDragging) {
      const r1 = Math.min(selection.startRow, selection.endRow)
      const c1 = Math.min(selection.startCol, selection.endCol)
      const fillValue = data[r1][c1]
      applyFillWithValue(fillValue)
    }
    isDragging = false
    isHandleDragging = false
    updateOverlay()
  }
  document.removeEventListener('mousemove', onPointerMove)
  document.removeEventListener('mouseup', onDocMouseUp)
}

/* doc mouse move bound to optimized handler */
function onDocMouseMove(e) {
  // for resizing
  if (isColResizing && resizeInfo) {
    const deltaX = e.clientX - resizeInfo.startX
    const newSize = Math.max(24, resizeInfo.startSize + deltaX)
    colWidths[resizeInfo.index] = Math.min(newSize, 1000)
    updateOverlay()
    return
  }
  if (isRowResizing && resizeInfo) {
    const deltaY = e.clientY - resizeInfo.startY
    const newSize = Math.max(18, resizeInfo.startSize + deltaY)
    rowHeights[resizeInfo.index] = Math.min(newSize, 1000)
    updateOverlay()
    return
  }
}

/* start col resize */
function startColResize(e, colIndex) {
  isColResizing = true
  resizeInfo = { type: 'col', index: colIndex, startX: e.clientX, startSize: colWidths[colIndex] }
  document.addEventListener('mousemove', onDocMouseMove)
  document.addEventListener('mouseup', onDocMouseUp)
}

/* start row resize */
function startRowResize(e, rowIndex) {
  isRowResizing = true
  resizeInfo = { type: 'row', index: rowIndex, startY: e.clientY, startSize: rowHeights[rowIndex] }
  document.addEventListener('mousemove', onDocMouseMove)
  document.addEventListener('mouseup', onDocMouseUp)
}

/* resize hint helpers (optional UI nicety) */
function maybeShowColResize(e, colIndex) {
  const rect = e.currentTarget.getBoundingClientRect()
  const offset = rect.right - e.clientX
  e.currentTarget.style.cursor = offset < 8 ? 'col-resize' : 'default'
}
function hideColResizeHint(colIndex) { /* no-op for now */ }
function maybeShowRowResize(e, rowIndex) {
  const rect = e.currentTarget.getBoundingClientRect()
  const offset = rect.bottom - e.clientY
  e.currentTarget.style.cursor = offset < 6 ? 'row-resize' : 'default'
}
function hideRowResizeHint(rowIndex) { /* no-op for now */ }

/* drag handle for selection fill */
function dragHandleMouseDown(e, r, c) {
  if (ACCESS_MODE.value === 'view') return
  isHandleDragging = true
  document.addEventListener('mousemove', onPointerMove)
  document.addEventListener('mouseup', onDocMouseUp)
}

/* selection mouse down (start drag) */
function startSelectionMouse(e) {
  document.addEventListener('mousemove', onPointerMove)
  document.addEventListener('mouseup', onDocMouseUp)
}

/* apply fill (copy value into all cells in selection) */
function applyFillWithValue(value) {
  if (!selection.active) return
  const r1 = Math.min(selection.startRow, selection.endRow)
  const r2 = Math.max(selection.startRow, selection.endRow)
  const c1 = Math.min(selection.startCol, selection.endCol)
  const c2 = Math.max(selection.startCol, selection.endCol)
  for (let rr = r1; rr <= r2; rr++) {
    for (let cc = c1; cc <= c2; cc++) {
      data[rr][cc] = value
      enqueueChange(rr, cc, value)
    }
  }
  updateOverlay()
}

/* on input blur -> enqueue change */
function onInputBlur(r, c) {
  selection.editing = false
  enqueueChange(r, c, data[r][c])
}

/* on input focus */
function onInputFocus(r, c) {
  selection.editing = true
  selection.startRow = r
  selection.startCol = c
  selection.endRow = r
  selection.endCol = c
  selection.active = true
  updateOverlay()
}

/* ENQUEUE changes for batch */
function enqueueChange(r, c, value) {
  const key = `${r}:${c}`
  pendingChanges.set(key, { r, c, value })
}

/* periodic flush (sends via websocket if available, else console.log) */
function flushPendingChanges() {
  if (pendingChanges.size === 0) return
  const batch = Array.from(pendingChanges.values())
  pendingChanges.clear()
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify({ type: 'batch', payload: batch }))
  } else {
    console.log('batch changes (no ws):', batch)
  }
}

/* ADD ROWS/COLUMNS with limits */
function addRows(count = 1) {
  const toAdd = clamp(Number(count) || 1, 1, MAX_ROWS - rows.value.length)
  for (let i = 0; i < toAdd; i++) {
    rows.value.push({})
    rowHeights.push(28)
    data.push(Array(columns.value.length).fill(''))
  }
}
function addColumns(count = 1) {
  const toAdd = clamp(Number(count) || 1, 1, MAX_COLS - columns.value.length)
  const startIndex = columns.value.length
  for (let i = 0; i < toAdd; i++) {
    columns.value.push(getColumnName(startIndex + i))
    colWidths.push(cellWidthDefault)
  }
  data.forEach((row) => {
    for (let i = 0; i < toAdd; i++) row.push('')
  })
}

/* compute sizes and offsets (cache) */
function recomputeLayout() {
  // header height (if header present)
  headerHeight = headerRef.value ? headerRef.value.getBoundingClientRect().height : 0
  leftStickyWidth = 50 // row header fixed width (could compute from DOM)
  cellWidthDefault = colWidths[0] || 90
  cellHeightDefault = rowHeights[0] || 28
  updateOverlay()
}

/* pointer/scroll handlers */
function onScroll() { updateOverlay() }

/* selection helpers for template */
function isSelectionActiveAt(r, c) { return selection.active && r === Math.max(selection.startRow, selection.endRow) && c === Math.max(selection.startCol, selection.endCol) }

/* ===== WEBSOCKET: connect to backend and handle messages ===== */
function initWebSocket(projectId = 'demo') {
  try {
    ws = new WebSocket(`${WS_URL}/${projectId}`)
    ws.onopen = () => console.log('WS connected')
    ws.onmessage = (ev) => {
      // handle messages from server — for example, patches, remote edits
      const msg = JSON.parse(ev.data)
      // TODO: implement handling of types: 'patch', 'sync', 'error'
      console.log('WS message', msg)
    }
    ws.onclose = () => console.log('WS closed')
    ws.onerror = (err) => console.error('WS error', err)
  } catch (err) {
    console.error('WS init failed', err)
  }
}

/* ===== LIFECYCLE ===== */
onMounted(() => {
  // init layout cache
  recomputeLayout()
  window.addEventListener('resize', recomputeLayout)

  // global mouse handlers (for selection/resizing)
  document.addEventListener('mousedown', startSelectionMouse)
  document.addEventListener('mousemove', onPointerMove)
  document.addEventListener('mouseup', onDocMouseUp)

  // batch flush interval
  batchInterval = setInterval(flushPendingChanges, BATCH_INTERVAL)

  // open websocket (replace project id with real)
  initWebSocket('demo')
})

onUnmounted(() => {
  // cleanup
  window.removeEventListener('resize', recomputeLayout)
  document.removeEventListener('mousedown', startSelectionMouse)
  document.removeEventListener('mousemove', onPointerMove)
  document.removeEventListener('mouseup', onDocMouseUp)
  clearInterval(batchInterval)
  if (ws) ws.close()
})
</script>

<style scoped>
/* Minimalist white look + light grid (like Google Sheets) */
.spreadsheet-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: white; /* removed background */
  font-family: "Segoe UI", Arial, sans-serif;
}

/* header larger */
.spreadsheet-header {
  height: 64px;
  border-bottom: 1px solid #e6e6e6;
  background: white;
  position: sticky;
  top: 0;
  z-index: 20;
}

/* grid wrapper */
.grid-wrapper {
  flex: 1;
  overflow: auto;
  position: relative;
  background: white;
}

/* table */
.spreadsheet {
  border-collapse: collapse;
  width: max-content;
  min-width: 100%;
  background: white;
}

/* thin light grid lines (Google Sheets feel) */
th, td {
  border: 1px solid rgba(0,0,0,0.08);
  padding: 0;
  box-sizing: border-box;
  background: white;
}

/* corner */
.corner-cell {
  min-width: 50px;
  background: white;
}

/* column header */
.col-header {
  position: sticky;
  top: 64px; /* under the header */
  z-index: 10;
  text-align: center;
  min-width: 60px;
  height: 32px;
  line-height: 32px;
  padding: 0 6px;
}

/* column inner to center label */
.col-inner { pointer-events:none; user-select:none; }

/* column resizer handle */
.col-resizer {
  position: absolute;
  right: 0;
  top: 0;
  width: 6px;
  height: 100%;
  cursor: col-resize;
  z-index: 30;
}

/* row header */
.row-header {
  position: sticky;
  left: 0;
  z-index: 12;
  min-width: 50px;
  text-align: center;
  padding: 0;
}

/* row resizer */
.row-resizer {
  position: absolute;
  bottom: 0;
  left: 0;
  height: 6px;
  width: 100%;
  cursor: row-resize;
  z-index: 30;
}

/* cell sizes */
td { vertical-align: top; }

/* input cell */
td input {
  width: 100%;
  height: 100%;
  border: none;
  padding: 6px 8px;
  box-sizing: border-box;
  background: white;
  font-size: 13px;
  caret-color: #333;
}

/* view-only cell */
.cell-view {
  padding: 6px 8px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* selection visuals */
.cell-selected {
  background: rgba(60, 170, 80, 0.04);
  /* inner thin border */
  box-shadow: inset 0 0 0 1px rgba(60,170,80,0.6);
}

/* show handle on bottom-right */
.cell-handle-visible .drag-handle {
  display: block;
}

/* drag handle */
.drag-handle {
  position: absolute;
  bottom: 3px;
  right: 3px;
  width: 10px;
  height: 10px;
  background: #4caf50;
  border-radius: 1px;
  cursor: nwse-resize;
  display: none;
  z-index: 40;
}

/* add-controls sticky */
.add-controls { display:flex; gap:6px; align-items:center; justify-content:center; padding:6px; }
.add-controls input { width:60px; padding:4px; border-radius:4px; border:1px solid #ddd; text-align:center; }
.add-controls button { padding:6px 8px; background:#0b69ff; color:white; border:none; border-radius:6px; cursor:pointer; }

/* sticky placements */
.sticky-right { position: sticky; right: 0; background: white; z-index: 15; min-width:160px; }
.sticky-bottom { position: sticky; bottom: 0; background: white; z-index: 15; height: 44px; }
.sticky-bottom-left { position: sticky; bottom:0; left:0; background: white; z-index: 16; padding: 6px; }

/* overlay selection */
.selection-overlay {
  position: absolute;
  border: 2px solid rgba(76,175,80,0.95);
  background: rgba(76,175,80,0.06);
  pointer-events: none;
  z-index: 50;
  box-sizing: border-box;
  border-radius: 3px;
}

/* view-only styling */
.view-only td input { pointer-events: none; }

/* cursor rules */
.spreadsheet td { cursor: default; } /* default cursor on cells */
.spreadsheet input:focus { cursor: text; } /* text cursor when editing */
</style>
