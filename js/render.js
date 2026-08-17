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
  var N = 0;

  function buildBoard(size) {
    boardEl.textContent = "";
    N = size;
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

  /** pieces: 길이 3 배열, 빈 칸은 null. grow=true 면 커지며 나타난다. */
  function drawTray(pieces, scale, grow) {
    for (var i = 0; i < 3; i++) {
      var slot = document.querySelector('.slot[data-slot="' + i + '"]');
      slot.textContent = "";
      if (!pieces[i]) continue;
      var el = pieceEl(pieces[i], scale);
      if (grow) el.classList.add("in");
      slot.appendChild(el);
    }
  }

  /** 트레이의 블록들을 줄어들며 사라지게 한다 (모델은 건드리지 않는다) */
  function trayOut() {
    var blocks = document.querySelectorAll(".slot > .block");
    for (var i = 0; i < blocks.length; i++) blocks[i].classList.add("out");
  }

  /** 보드 전체를 다시 그린다. 64칸뿐이라 델타 추적할 값어치가 없다. */
  function paintBoard(get) {
    for (var r = 0; r < N; r++) {
      for (var c = 0; c < N; c++) {
        var el = boardEl.children[r * N + c];
        var data = get(r, c);
        var want = data ? tileUrl(data.color, data.h) : "";
        if (el.dataset.tile === want) continue;
        el.dataset.tile = want;
        el.textContent = "";
        if (data) {
          var t = document.createElement("div");
          t.className = "tile";
          t.style.backgroundImage = want;
          el.appendChild(t);
        }
      }
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
    paintBoard: paintBoard,
    pieceEl: pieceEl,
    drawTray: drawTray,
    trayOut: trayOut,
    setScore: setScore,
    setGauge: setGauge,
    setLowTime: setLowTime
  };
})();
