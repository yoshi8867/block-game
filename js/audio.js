/* 사운드. 브라우저가 사용자 제스처 전 재생을 막으므로 시작 화면 탭에서 깨운다.
   같은 효과음이 연달아 나면 currentTime 을 되감아 다시 튼다. */
var Sound = (function () {
  "use strict";

  /* sfx_lineclear 는 넣지 않는다. 원본 wav 를 원본 트랙과 상호상관으로 대조해 보니
     sfx_nice(8.749~10.169초) 안에 sfx_lineclear(9.250~10.100초)가 통째로 들어 있다.
     즉 '줄 삭제음'이 아니라 nice 소리의 뒷부분을 잘라낸 것이다.
     nice/perfect 두 음원 모두 앞머리 0.04~0.10초에 줄 터지는 소리를 이미 갖고 있다. */
  var NAMES = ["intro", "bgm_loop", "sfx_nice",
               "sfx_perfect", "sfx_timebonus", "sfx_gameover"];

  var el = {};
  var ready = false;
  var introTimer = 0;

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
    // 아직 한 번도 안 튼 요소에 currentTime 을 쓰면 브라우저에 따라 던진다.
    if (a.currentTime) a.currentTime = 0;
    var p = a.play();
    if (p && p.catch) p.catch(function () {});
  }

  /** 인트로를 틀고, 끝나면 바로 BGM 루프로 넘어간다 (원작 그대로).
      음원의 '띠' 는 0.050 / 1.060 / 2.060(긴소리) 세 번뿐이다 — '3' 에 해당하는
      첫 비프가 없다. 그래서 카운트다운 텍스트보다 CONFIG.INTRO_DELAY_MS 만큼
      늦게 틀어 긴 '띠—' 가 GO! 와 겹치게 한다. (tools/intro_beeps.py 로 실측) */
  function startMusic() {
    clearTimeout(introTimer);
    el.bgm_loop.pause();
    el.bgm_loop.currentTime = 0;
    el.intro.onended = function () { play("bgm_loop"); };
    introTimer = setTimeout(function () { play("intro"); }, CONFIG.INTRO_DELAY_MS);
  }

  function stopMusic() {
    clearTimeout(introTimer);
    el.intro.onended = null;
    el.intro.pause();
    el.bgm_loop.pause();
  }

  return { unlock: unlock, play: play, startMusic: startMusic, stopMusic: stopMusic };
})();
