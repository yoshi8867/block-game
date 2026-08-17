/* 줄 삭제 연출 — NICE!/PERFECT! 배너 + 칸마다 튀는 파편.

   원작 실측: 배너는 항상 같은 자리(무대 중앙 x, 보드 첫 줄 높이)에 뜨고
   0.60초 동안 살짝 커졌다가 페이드 없이 사라진다.
   파편은 30fps 기준 2프레임(≈67ms)뿐이라 60Hz에서 보이게 조금 늘렸다. */
var FX = (function () {
  "use strict";

  var bannerEl = document.getElementById("banner");
  var boardEl = document.getElementById("board");

  var BANNER_MS = 600;
  var SHARDS = 8;
  var SHARD_MS = 160;

  /* 파편 색. 원작에서 노란 칸 → 금색, 보라 칸 → 분홍으로 확인했다.
     하늘/분홍 칸은 그 장면이 안 나와 같은 규칙(밝은 쪽으로 한 단계)으로 정했다. */
  var SHARD_COLOR = {
    yellow: "#FFC93C",
    purple: "#FF7BD5",
    cyan: "#7DE8FF",
    pink: "#FFA0DC"
  };

  /* 카운트다운. 원작은 3·2·1·GO! 가 각각 1.0초씩, 확대 같은 움직임 없이 그냥 바뀐다.
     글자는 폰트가 아니라 영상에서 잘라낸 이미지다 (tools/intro_crop.py). */
  function showCount(kind) {
    bannerEl.textContent = "";
    var img = document.createElement("img");
    img.src = "assets/cd" + kind + ".png";
    img.className = "count-art c" + kind;
    bannerEl.appendChild(img);
  }

  function clear() {
    bannerEl.textContent = "";
  }

  function showBanner(kind) {
    bannerEl.textContent = "";
    var img = document.createElement("img");
    img.src = "assets/banner_" + kind + ".png";
    img.className = "banner-art " + kind;
    bannerEl.appendChild(img);
    setTimeout(function () { if (img.parentNode) img.remove(); }, BANNER_MS);
  }

  /* 원작에선 NICE!/PERFECT! **아래**에 겹쳐 뜬다. 그래서 배너를 지우지 않고 얹는다.
     onPlace 가 showBanner 를 먼저 부르므로 순서는 저절로 맞는다. */
  function showTimeBonus() {
    var img = document.createElement("img");
    img.src = "assets/banner_timebonus.png";
    img.className = "banner-art timebonus";
    bannerEl.appendChild(img);
    setTimeout(function () { if (img.parentNode) img.remove(); }, BANNER_MS);
  }

  /** cells: Board.clearLines() 가 돌려준 [{r,c,color,h}] */
  function burst(cells) {
    for (var i = 0; i < cells.length; i++) {
      var cell = cells[i];
      var host = boardEl.children[cell.r * CONFIG.BOARD + cell.c];
      var box = document.createElement("div");
      box.className = "burst";
      for (var s = 0; s < SHARDS; s++) {
        var sh = document.createElement("div");
        sh.className = "shard";
        sh.style.setProperty("--a", (s * 360 / SHARDS + (i % 2) * 22) + "deg");
        sh.style.setProperty("--c", SHARD_COLOR[cell.color] || "#fff");
        box.appendChild(sh);
      }
      host.appendChild(box);
      remove(box);
    }
  }

  function remove(el) {
    setTimeout(function () { if (el.parentNode) el.remove(); }, SHARD_MS);
  }

  return { showBanner: showBanner, showTimeBonus: showTimeBonus,
           burst: burst, showCount: showCount, clear: clear };
})();
