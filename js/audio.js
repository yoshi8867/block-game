/* 사운드. 브라우저가 사용자 제스처 전 재생을 막으므로 시작 화면 탭에서 깨운다.
   같은 효과음이 연달아 나면 currentTime 을 되감아 다시 튼다. */
var Sound = (function () {
  "use strict";

  var NAMES = ["intro", "bgm_loop", "sfx_lineclear", "sfx_nice",
               "sfx_perfect", "sfx_timebonus", "sfx_gameover"];

  var el = {};
  var ready = false;

  for (var i = 0; i < NAMES.length; i++) {
    var a = new Audio("audio/" + NAMES[i] + ".mp3");
    a.preload = "auto";
    el[NAMES[i]] = a;
  }
  el.bgm_loop.loop = true;

  /** 시작 화면 탭에서 부른다.
     iOS/사파리는 요소마다 '제스처 안에서 한 번 재생된 적'이 있어야 나중에
     코드로 재생할 수 있다. 그래서 효과음을 무음으로 한 번 틀었다 세운다.
     intro/bgm 은 바로 이어서 정상 재생하므로 건드리지 않는다. */
  function unlock() {
    if (ready) return;
    ready = true;
    el.bgm_loop.volume = CONFIG.BGM_VOLUME;
    el.intro.volume = CONFIG.SFX_VOLUME;

    NAMES.forEach(function (n) {
      if (n === "intro" || n === "bgm_loop") return;
      var a = el[n];
      a.volume = 0;

      function done() {
        a.pause();
        a.currentTime = 0;
        a.volume = CONFIG.SFX_VOLUME;
      }

      var p = a.play();
      if (p && p.then) p.then(done, done);
      else done();
    });
  }

  function play(name) {
    var a = el[name];
    a.currentTime = 0;
    var p = a.play();
    if (p && p.catch) p.catch(function () {});
  }

  /** 인트로를 틀고, 끝나면 바로 BGM 루프로 넘어간다 (원작 그대로) */
  function startMusic() {
    el.bgm_loop.pause();
    el.bgm_loop.currentTime = 0;
    el.intro.onended = function () { play("bgm_loop"); };
    play("intro");
  }

  function stopMusic() {
    el.intro.onended = null;
    el.intro.pause();
    el.bgm_loop.pause();
  }

  return { unlock: unlock, play: play, startMusic: startMusic, stopMusic: stopMusic };
})();
