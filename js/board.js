/* 8×8 보드 모델. DOM 을 모른다 — 렌더는 render.js 가 한다. */
var Board = (function () {
  "use strict";

  var N = 0;
  var grid = [];

  function reset(n) {
    N = n;
    grid = [];
    for (var r = 0; r < n; r++) {
      var row = [];
      for (var c = 0; c < n; c++) row.push(null);
      grid.push(row);
    }
  }

  function get(r, c) { return grid[r][c]; }

  /** piece 의 좌상단을 (r0,c0)에 놓을 수 있나 */
  function canPlace(piece, r0, c0) {
    for (var i = 0; i < piece.cells.length; i++) {
      var r = r0 + piece.cells[i].r;
      var c = c0 + piece.cells[i].c;
      if (r < 0 || c < 0 || r >= N || c >= N) return false;
      if (grid[r][c]) return false;
    }
    return true;
  }

  function place(piece, r0, c0) {
    for (var i = 0; i < piece.cells.length; i++) {
      var cell = piece.cells[i];
      grid[r0 + cell.r][c0 + cell.c] = { color: piece.color, h: cell.h };
    }
  }

  /** 어디든 놓을 자리가 있나 (데드락 판정용) */
  function anyFit(piece) {
    for (var r = 0; r < N; r++)
      for (var c = 0; c < N; c++)
        if (canPlace(piece, r, c)) return true;
    return false;
  }

  /** 꽉 찬 줄. { rows:[], cols:[] } */
  function fullLines() {
    var rows = [], cols = [], r, c, full;
    for (r = 0; r < N; r++) {
      for (full = true, c = 0; c < N; c++) if (!grid[r][c]) { full = false; break; }
      if (full) rows.push(r);
    }
    for (c = 0; c < N; c++) {
      for (full = true, r = 0; r < N; r++) if (!grid[r][c]) { full = false; break; }
      if (full) cols.push(c);
    }
    return { rows: rows, cols: cols };
  }

  /** 줄을 지우고 지워진 칸 목록을 돌려준다. 교차 칸도 한 번만 들어간다. */
  function clearLines(lines) {
    var seen = {}, out = [], i, r, c;

    function take(r, c) {
      var k = r + "," + c;
      if (seen[k] || !grid[r][c]) return;
      seen[k] = 1;
      out.push({ r: r, c: c, color: grid[r][c].color, h: grid[r][c].h });
    }

    for (i = 0; i < lines.rows.length; i++)
      for (c = 0; c < N; c++) take(lines.rows[i], c);
    for (i = 0; i < lines.cols.length; i++)
      for (r = 0; r < N; r++) take(r, lines.cols[i]);

    for (i = 0; i < out.length; i++) grid[out[i].r][out[i].c] = null;
    return out;
  }

  /** 완성한 줄에 포함된 h 칸 수. 교차 칸이 h면 두 줄 모두에 카운트한다. */
  function countH(lines) {
    var n = 0, i, r, c;
    for (i = 0; i < lines.rows.length; i++)
      for (c = 0; c < N; c++) if (grid[lines.rows[i]][c] && grid[lines.rows[i]][c].h) n++;
    for (i = 0; i < lines.cols.length; i++)
      for (r = 0; r < N; r++) if (grid[r][lines.cols[i]] && grid[r][lines.cols[i]].h) n++;
    return n;
  }

  return {
    reset: reset, get: get,
    canPlace: canPlace, place: place, anyFit: anyFit,
    fullLines: fullLines, clearLines: clearLines, countH: countH
  };
})();
