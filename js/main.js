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

  // 이 점수를 넘는 순간 효과음 + 글자만 (시간은 안 준다).
  // 원작 실측: 두 영상 모두 5,000 과 7,000 에서 딱 한 번씩 뜬다
  // (6,860→8,920 은 7,000·8,000 을 함께 넘는데도 한 번뿐이었다).
  // tools/score_audit.py 참조.
  TIME_BONUS_AT: [5000, 7000],

  // block change 총 대기. 앞 절반은 줄어들며 사라지고, 뒤 절반은 커지며 나타난다.
  // 절반값은 css/ui.css 의 trayOut/trayIn 애니메이션 길이와 같아야 한다.
  BLOCK_CHANGE_MS: 1000,
  COUNT_MS: 1000,          // 카운트다운 한 단계 (원작 실측 정확히 1.0초)

  BGM_VOLUME: 0.45,
  SFX_VOLUME: 1.0,

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
  var endAt = 0;         // performance.now() 기준 종료 시각
  var raf = 0;
  var changeTimer = 0;   // block change 대기 중이면 setTimeout 핸들
  var changeBtn = document.getElementById("block-change");

  function refillTray(grow) {
    for (var i = 0; i < 3; i++) {
      if (!tray[i]) tray[i] = Blocks.random(CONFIG.H_CHANCE);
    }
    Render.drawTray(tray, CONFIG.TRAY_SCALE, grow);
  }

  /** block change: 앞 절반 동안 블록이 줄어들며 사라지고, 뒤 절반 동안 새 블록이
      커지며 나타난다. 그 1초 내내 아무것도 못 놓는 게 패널티다. 횟수 제한은 없다.
      애니메이션 길이는 css/ui.css 의 trayOut/trayIn 과 맞춰야 한다. */
  function blockChange() {
    if (changeTimer) return;                 // 대기 중 연타 무시
    if (stage.classList.contains("locked")) return;   // 카운트다운 중 · 종료 후
    var half = CONFIG.BLOCK_CHANGE_MS / 2;
    Drag.cancel();
    tray = [null, null, null];               // 모델은 즉시 비운다 (집을 수 없게)
    Render.trayOut();                        // 화면의 블록은 줄어들며 사라진다
    changeBtn.disabled = true;
    changeTimer = setTimeout(function () {
      refillTray(true);                      // 커지며 등장
      changeTimer = setTimeout(function () {
        changeTimer = 0;
        changeBtn.disabled = false;
      }, half);
    }, half);
  }

  /** 대기 중이던 리필을 취소한다 (새 판 / 게임오버).
      사라지는 중이었으면 블록이 안 보인 채 굳으므로 다시 그려 준다. */
  function cancelChange() {
    if (changeTimer) {
      clearTimeout(changeTimer);
      changeTimer = 0;
      refillTray();
    }
    changeBtn.disabled = false;
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
      // nice/perfect 음원 앞머리에 줄 터지는 소리가 이미 들어 있다.
      // 따로 lineclear 를 겹치면 같은 소리가 두 번 난다 (아래 audio.js 주석 참조).
      Sound.play(hits ? "sfx_perfect" : "sfx_nice");
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

  /** 실제 시간은 주지 않는다. 소리와 글자만 (사용자 확정).
      원작대로 NICE!/PERFECT! 와 **동시에** 뜨고 소리도 겹쳐서 난다. */
  function timeBonus() {
    Sound.play("sfx_timebonus");
    FX.showTimeBonus();
  }

  /* ── 타이머 ────────────────────────────────────────── */

  function tick() {
    var left = (endAt - performance.now()) / 1000;
    if (left <= 0) { Render.setGauge(0); gameOver(); return; }
    Render.setGauge(left / CONFIG.PLAY_SECONDS);
    Render.setLowTime(left <= CONFIG.LOW_TIME_SECONDS);
    raf = requestAnimationFrame(tick);
  }

  function startClock() {
    endAt = performance.now() + CONFIG.PLAY_SECONDS * 1000;
    cancelAnimationFrame(raf);
    tick();
  }

  function gameOver() {
    cancelAnimationFrame(raf);
    cancelChange();
    Drag.cancel();
    Render.setLowTime(false);
    stage.classList.add("locked", "over");
    Sound.stopMusic();
    Sound.play("sfx_gameover");
  }

  /* ── 인트로 카운트다운 ─────────────────────────────── */

  function runIntro(done) {
    var steps = ["3", "2", "1", "go"];
    var i = 0;
    stage.classList.add("locked");
    (function next() {
      if (i === steps.length) {
        FX.clear();
        stage.classList.remove("locked");
        done();
        return;
      }
      FX.showCount(steps[i++]);
      setTimeout(next, CONFIG.COUNT_MS);
    })();
  }

  /** 새 판. 시작 화면 탭과 RETRY 가 공유한다. */
  function newGame() {
    cancelAnimationFrame(raf);
    cancelChange();
    stage.classList.remove("over");
    Drag.cancel();
    Board.reset(CONFIG.BOARD);
    Render.paintBoard(Board.get);
    score = 0;
    Render.setScore(0);
    Render.setGauge(1);
    Render.setLowTime(false);
    tray = [null, null, null];
    refillTray();
    Sound.startMusic();          // intro → 끝나면 bgm 루프
    runIntro(startClock);
  }

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
    Sound.unlock();      // 이 탭이 유일한 사용자 제스처다. 여기서 재생 권한을 딴다
    newGame();
  }

  /* 처음 쓰는 이미지는 그때 받아서 디코드하느라 한 박자 늦게 떴다 —
     첫 NICE!/PERFECT! 배너가 툭 튀고, 블록의 마지막 칸이 뒤늦게 채워졌다.
     페이지가 열릴 때 전부 받아 디코드까지 끝내 둔다.
     keep 에 담아 두지 않으면 GC 가 디코드 결과를 버려서 도로 늦어진다. */
  var keep = [];

  function preloadImages() {
    var names = ["banner_nice", "banner_perfect", "banner_timebonus",
                 "cd3", "cd2", "cd1", "cdgo", "gameover"];
    ["purple", "cyan", "yellow", "pink"].forEach(function (c) {
      names.push("cell_" + c, "cell_" + c + "_h");
    });
    names.forEach(function (n) {
      var img = new Image();
      img.src = "assets/" + n + ".png";
      if (img.decode) img.decode().catch(function () {});
      keep.push(img);
    });
  }

  function init() {
    preloadImages();
    Board.reset(CONFIG.BOARD);
    Render.buildBoard(CONFIG.BOARD);
    Drag.init({ getPiece: function (i) { return tray[i]; }, onPlace: onPlace });
    Render.setScore(0);
    Render.setGauge(1);
    refillTray();               // 시작 화면 뒤로 미리 보이게

    document.getElementById("start").addEventListener("click", start);
    document.getElementById("retry").addEventListener("click", newGame);

    // ?dev — 시작 화면과 카운트다운을 건너뛴다. 레이아웃 대조용.
    if (/[?&]dev\b/.test(location.search)) {
      stage.classList.add("started");
      score = 25815;
      Render.setScore(score);
      startClock();
    }
    changeBtn.addEventListener("click", blockChange);

    /* 테스트용 툴바. index.html 의 #devbar 주석과 짝이다 — 다시 쓰려면 둘 다 푼다.
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
    document.getElementById("dev-end").addEventListener("click", gameOver);
    // 남은 시간을 경고 직전으로 당긴다
    document.getElementById("dev-low").addEventListener("click", function () {
      endAt = performance.now() + CONFIG.LOW_TIME_SECONDS * 1000;
    });
    */

    // ?auto=fx|end|clear — 헤드리스 스크린샷용. 0.9초 뒤 해당 테스트 버튼을 누른다.
    var auto = /[?&]auto=([a-z,-]+)/.exec(location.search);
    if (auto) {
      auto[1].split(",").forEach(function (name, i) {
        setTimeout(function () {
          var b = document.getElementById("dev-" + name) ||
                  document.getElementById(name);
          if (b) b.click();
        }, 900 + i * 400);
      });
    }
  }

  return { init: init };
})();

Game.init();
