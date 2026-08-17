/* 포인터 드래그 · 배치 판정.
   원칙(사용자 확정):
   - 잡은 지점의 상대 위치를 그대로 유지한다. 손가락 기준 중앙 정렬은 하지 않는다
   - 트레이 0.54배 → 집어 올리면 보드와 1:1. 확대 기준점은 잡은 지점
   - 판정은 손가락이 아니라 블록이 실제로 겹쳐 보이는 위치 기준.
     블록 전체를 통째로 정수 칸 단위 반올림한다 (반올림 자체가 ±반칸 관용)
   - 미리보기 없음. 무효면 즉시 원위치, 애니메이션 없음 */
var Drag = (function () {
  "use strict";

  var stage = document.getElementById("stage");
  var layer = document.getElementById("drag-layer");
  var boardEl = document.getElementById("board");

  var api = null;   // { getPiece(i), onPlace(i, piece, r, c) }
  var cur = null;

  function clamp01(v) { return v < 0 ? 0 : v > 1 ? 1 : v; }

  /** 보드 밖으로 조금 삐져나간 블록을 안으로 끌어당긴다.
     가장자리 줄은 바깥으로 밀 여지가 없어 실질 허용치가 절반뿐이라서.
     CONFIG.EDGE_PULL = 0 이면 끈다. */
  function pull(v, span) {
    var lim = CONFIG.EDGE_PULL;
    var max = CONFIG.BOARD - span;
    if (v < 0) return v >= -lim ? 0 : v;
    if (v > max) return v <= max + lim ? max : v;
    return v;
  }

  /** 보드 칸 격자를 실측한다. 창 크기가 바뀌어도 항상 맞는다. */
  function geom() {
    var a = boardEl.children[0].getBoundingClientRect();
    var b = boardEl.children[1].getBoundingClientRect();
    return { left: a.left, top: a.top, pitch: b.left - a.left };
  }

  function down(e) {
    // locked = 카운트다운 중이거나 게임이 끝났다
    if (cur || !stage.classList.contains("started")) return;
    if (stage.classList.contains("locked")) return;
    if (!e.target.closest) return;

    // 집는 판정은 블록이 아니라 슬롯 전체다. 1×1 블록을 정확히 찍기 어려워서.
    var slotEl = e.target.closest(".slot");
    if (!slotEl) return;

    var src = slotEl.querySelector(".block");
    var slot = +slotEl.dataset.slot;
    var piece = api.getPiece(slot);
    if (!src || !piece) return;

    // 잡은 지점을 블록 안의 비율로 기억한다 — 확대해도 같은 칸이 손가락 아래 남는다.
    // ponytail: 블록 바깥을 찍었으면 가장 가까운 모서리를 잡은 것으로 친다
    var r = src.getBoundingClientRect();
    var el = Render.pieceEl(piece, 1);
    el.className += " dragging";
    layer.appendChild(el);
    var full = el.getBoundingClientRect();

    cur = {
      slot: slot, piece: piece, el: el, src: src,
      fx: clamp01((e.clientX - r.left) / r.width),
      fy: clamp01((e.clientY - r.top) / r.height),
      w: full.width, h: full.height
    };
    src.style.visibility = "hidden";
    move(e);
    e.preventDefault();
  }

  function move(e) {
    if (!cur) return;
    var s = stage.getBoundingClientRect();
    var lift = CONFIG.DRAG_LIFT * s.width;
    cur.el.style.left = (e.clientX - cur.fx * cur.w - s.left) + "px";
    cur.el.style.top = (e.clientY - cur.fy * cur.h - s.top - lift) + "px";
  }

  function up() {
    if (!cur) return;
    var c = cur;
    cur = null;

    var box = c.el.getBoundingClientRect();
    var g = geom();
    var r0 = pull(Math.round((box.top - g.top) / g.pitch), c.piece.rows);
    var c0 = pull(Math.round((box.left - g.left) / g.pitch), c.piece.cols);
    c.el.remove();

    if (Board.canPlace(c.piece, r0, c0)) {
      c.src.remove();
      api.onPlace(c.slot, c.piece, r0, c0);
    } else {
      c.src.style.visibility = "";   // 즉시 원위치
    }
  }

  function cancel() {
    if (!cur) return;
    cur.el.remove();
    cur.src.style.visibility = "";
    cur = null;
  }

  function init(hooks) {
    api = hooks;
    stage.addEventListener("pointerdown", down);
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
    window.addEventListener("pointercancel", cancel);
  }

  return { init: init, cancel: cancel };
})();
