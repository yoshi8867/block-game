/* DOM 생성 / 갱신. 게임 로직은 담지 않는다.
   길이 단위는 cqw = 무대 가로폭의 1%. #stage 가 container-type:size 이므로
   어디에 붙어도 무대 기준으로 해석된다. */
var Render = (function () {
  "use strict";

  /* 원작 실측 (1080 기준): 칸 101px, 피치 108.43px */
  var CELL = 101 / 10.80;        // 9.3519 cqw
  var PITCH = 108.43 / 10.80;    // 10.0398 cqw

  var boardEl = document.getElementById("board");
  var stageEl = document.getElementById("stage");

  function buildBoard(size) {
    boardEl.textContent = "";
    for (var r = 0; r < size; r++) {
      for (var c = 0; c < size; c++) {
        var d = document.createElement("div");
        d.className = "cell";
        d.dataset.r = r;
        d.dataset.c = c;
        boardEl.appendChild(d);
      }
    }
  }

  function tileUrl(color, isH) {
    return 'url("assets/cell_' + color + (isH ? "_h" : "") + '.png")';
  }

  /** 조각 하나를 DOM으로. scale 1 = 보드 크기 */
  function pieceEl(piece, scale) {
    var cell = CELL * scale;
    var pitch = PITCH * scale;
    var el = document.createElement("div");
    el.className = "block";
    el.style.width = ((piece.cols - 1) * pitch + cell) + "cqw";
    el.style.height = ((piece.rows - 1) * pitch + cell) + "cqw";
    for (var i = 0; i < piece.cells.length; i++) {
      var cellData = piece.cells[i];
      var t = document.createElement("div");
      t.className = "tile";
      t.style.left = (cellData.c * pitch) + "cqw";
      t.style.top = (cellData.r * pitch) + "cqw";
      t.style.width = cell + "cqw";
      t.style.height = cell + "cqw";
      t.style.backgroundImage = tileUrl(piece.color, cellData.h);
      el.appendChild(t);
    }
    return el;
  }

  /** pieces: 길이 3 배열, 빈 칸은 null */
  function drawTray(pieces, scale) {
    for (var i = 0; i < 3; i++) {
      var slot = document.querySelector('.slot[data-slot="' + i + '"]');
      slot.textContent = "";
      if (pieces[i]) slot.appendChild(pieceEl(pieces[i], scale));
    }
  }

  function setScore(n) {
    document.getElementById("score").textContent = n;
  }

  function setGauge(ratio) {
    var f = Math.max(0, Math.min(1, ratio));
    document.getElementById("gauge-fill").style.transform = "scaleX(" + f + ")";
  }

  function setLowTime(on) {
    stageEl.classList.toggle("low-time", !!on);
  }

  return {
    CELL: CELL,
    PITCH: PITCH,
    buildBoard: buildBoard,
    pieceEl: pieceEl,
    drawTray: drawTray,
    setScore: setScore,
    setGauge: setGauge,
    setLowTime: setLowTime
  };
})();
