/* 게임 상태 · 타이머 · 배선.
   튜닝 상수는 전부 여기 CONFIG 한 곳에 모은다. */
var CONFIG = {
  BOARD: 8,

  PLAY_SECONDS: 95,        // 원작 실측 92초, 채택값 95초
  LOW_TIME_SECONDS: 10,    // 이 시점부터 시계·게이지 깜빡임

  H_CHANCE: 0.10,          // 칸마다 독립적으로 보너스(h) 칸이 될 확률
  TRAY_SCALE: 0.54,        // 트레이 블록 = 보드 칸의 몇 배인가 (원작 실측)

  SCORE_LINE: 800,         // 줄 하나 완성
  SCORE_H: 100,            // 완성한 줄에 포함된 h 칸 하나당
  SCORE_CELL: 15,          // 내려놓은 칸 하나당

  TIME_BONUS_AT: [6000, 9000],   // 이 점수를 넘는 순간 효과음만 (시간은 안 준다)

  BLOCK_CHANGE_MS: 1500,   // block change 리프레시 대기

  // 드래그 중 블록을 손가락보다 위로 띄우는 양 (무대 가로폭 비율).
  // 0 = 원작대로 잡은 지점 그대로. 손가락에 가려 안 보이면 0.06 정도로 올린다.
  DRAG_LIFT: 0,

  // 보드 밖으로 삐져나간 블록을 몇 칸까지 안으로 끌어당길지. 0 = 끔.
  EDGE_PULL: 1
};

var Game = (function () {
  "use strict";

  var stage = document.getElementById("stage");
  var tray = [null, null, null];
  var score = 0;

  function refillTray() {
    for (var i = 0; i < 3; i++) {
      if (!tray[i]) tray[i] = Blocks.random(CONFIG.H_CHANCE);
    }
    Render.drawTray(tray, CONFIG.TRAY_SCALE);
  }

  function rerollTray() {
    Drag.cancel();
    tray = [null, null, null];
    refillTray();
  }

  /** 점수 = 800×줄 + 100×(완성한 줄의 h 칸) + 15×내려놓은 칸 */
  function onPlace(slot, piece, r, c) {
    Board.place(piece, r, c);
    tray[slot] = null;

    var gain = CONFIG.SCORE_CELL * piece.cells.length;
    var lines = Board.fullLines();
    var n = lines.rows.length + lines.cols.length;

    if (n) {
      var hits = Board.countH(lines);          // 지우기 전에 세야 한다
      gain += CONFIG.SCORE_LINE * n + CONFIG.SCORE_H * hits;
      var cleared = Board.clearLines(lines);
      Render.paintBoard(Board.get);
      FX.burst(cleared);
      FX.showBanner(hits ? "perfect" : "nice");
    } else {
      Render.paintBoard(Board.get);
    }

    addScore(gain);
    refillTray();
  }

  function addScore(gain) {
    var before = score;
    score += gain;
    Render.setScore(score);
    for (var i = 0; i < CONFIG.TIME_BONUS_AT.length; i++) {
      var at = CONFIG.TIME_BONUS_AT[i];
      if (before < at && score >= at) timeBonus();
    }
  }

  /** 실제 시간은 주지 않는다. 효과음만 — 6단계에서 연결. */
  function timeBonus() {}

  /** 브라우저 주소창/하단바를 숨긴다. 사용자 제스처 안에서만 허용된다. */
  function goFullscreen() {
    var el = document.documentElement;
    var req = el.requestFullscreen || el.webkitRequestFullscreen;
    if (req) {
      try {
        var p = req.call(el, { navigationUI: "hide" });
        if (p && p.then) p.then(lockPortrait, function () {});
      } catch (e) { /* 지원 안 하면 그냥 넘어간다 */ }
    }
  }

  function lockPortrait() {
    if (screen.orientation && screen.orientation.lock) {
      screen.orientation.lock("portrait").catch(function () {});
    }
  }

  function start() {
    stage.classList.add("started");
    goFullscreen();
    refillTray();
  }

  function init() {
    Board.reset(CONFIG.BOARD);
    Render.buildBoard(CONFIG.BOARD);
    Drag.init({ getPiece: function (i) { return tray[i]; }, onPlace: onPlace });
    Render.setScore(0);
    Render.setGauge(1);
    refillTray();               // 시작 화면 뒤로 미리 보이게

    document.getElementById("start").addEventListener("click", start);

    // ?dev — 시작 화면을 건너뛴다. 레이아웃 대조용.
    if (/[?&]dev\b/.test(location.search)) {
      stage.classList.add("started");
      score = 25815;
      Render.setScore(score);
    }
    // 정식 동작(1.5초 대기)은 7단계에서. 지금은 즉시 리롤로 블록 확인용.
    document.getElementById("block-change").addEventListener("click", rerollTray);

    // 테스트용 툴바 (임시)
    var pull = document.getElementById("dev-pull");
    pull.addEventListener("click", function () {
      CONFIG.EDGE_PULL = CONFIG.EDGE_PULL ? 0 : 1;
      pull.textContent = "PULL " + (CONFIG.EDGE_PULL ? "ON" : "OFF");
    });
    document.getElementById("dev-clear").addEventListener("click", function () {
      Drag.cancel();
      Board.reset(CONFIG.BOARD);
      Render.paintBoard(Board.get);
      score = 0;
      Render.setScore(0);
    });
    // 줄 삭제 연출을 손으로 안 만들고 바로 보기 위한 버튼
    document.getElementById("dev-fx").addEventListener("click", function () {
      var colors = ["purple", "yellow", "cyan", "pink"];
      Drag.cancel();
      Board.reset(CONFIG.BOARD);
      for (var c = 0; c < 7; c++) {
        Board.place({ color: colors[c % 4], cells: [{ r: 0, c: 0, h: c % 3 === 0 }] }, 3, c);
      }
      Render.paintBoard(Board.get);
      onPlace(0, { color: "cyan", cells: [{ r: 0, c: 0, h: true }] }, 3, 7);
    });
    // ?fx — 헤드리스 스크린샷으로 연출을 확인하려고 자동 발사
    if (/[?&]fx\b/.test(location.search)) {
      setTimeout(function () { document.getElementById("dev-fx").click(); }, 900);
    }
  }

  return { init: init, rerollTray: rerollTray };
})();

Game.init();
