/* DOM 생성 / 갱신. 게임 로직은 담지 않는다. */
var Render = (function () {
  "use strict";

  var boardEl = document.getElementById("board");

  /** 8x8 빈 칸 생성 */
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

  function setScore(n) {
    document.getElementById("score").textContent = n;
  }

  /** 남은 시간 비율 0..1 */
  function setGauge(ratio) {
    var f = Math.max(0, Math.min(1, ratio));
    document.getElementById("gauge-fill").style.transform = "scaleX(" + f + ")";
  }

  function setLowTime(on) {
    document.getElementById("stage").classList.toggle("low-time", !!on);
  }

  return {
    buildBoard: buildBoard,
    setScore: setScore,
    setGauge: setGauge,
    setLowTime: setLowTime
  };
})();
