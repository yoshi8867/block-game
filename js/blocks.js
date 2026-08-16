/* 블록 정의.
   원작은 모양(회전 포함)마다 색이 고정이다 — docs/analysis.md 1절 참조.
   confirmed:false 인 4종은 영상에 한 번도 등장하지 않아 색상이 추정치다. */
var Blocks = (function () {
  "use strict";

  var DEFS = [
    /* ── purple ─────────────────────────── */
    { c: "purple", g: ["XXX"] },
    { c: "purple", g: ["XX", ".X"] },
    { c: "purple", g: [".X", ".X", "XX"] },
    { c: "purple", g: [".X.", "XXX"] },
    { c: "purple", g: ["X", "X", "X", "X"] },
    { c: "purple", g: ["X..", "XXX"] },
    { c: "purple", g: ["X..", "X..", "XXX"] },
    { c: "purple", g: ["XXX", "XXX", "XXX"] },
    { c: "purple", g: [".X", "XX", "X."], confirmed: false },

    /* ── cyan ───────────────────────────── */
    { c: "cyan", g: ["XX"] },
    { c: "cyan", g: ["X", "X", "X"] },
    { c: "cyan", g: ["..X", "XXX"] },
    { c: "cyan", g: ["X.", "X.", "XX"] },
    { c: "cyan", g: ["X.", "XX", ".X"] },
    { c: "cyan", g: ["XXX", ".X."] },
    { c: "cyan", g: ["..X", "..X", "XXX"] },
    { c: "cyan", g: ["XXX", "XXX"] },
    { c: "cyan", g: ["XX", "X."], confirmed: false },

    /* ── yellow ─────────────────────────── */
    { c: "yellow", g: ["X"] },
    { c: "yellow", g: ["X", "X"] },
    { c: "yellow", g: [".X", "XX"] },
    { c: "yellow", g: [".X", "XX", ".X"] },
    { c: "yellow", g: [".XX", "XX."] },
    { c: "yellow", g: ["XX", "X.", "X."] },
    { c: "yellow", g: ["XXX", "X.."] },
    { c: "yellow", g: ["XXX", "..X", "..X"] },
    { c: "yellow", g: ["XX", "XX", "XX"] },

    /* ── pink ───────────────────────────── */
    { c: "pink", g: ["X.", "XX", "X."] },
    { c: "pink", g: ["XX", "XX"] },
    { c: "pink", g: ["XX.", ".XX"] },
    { c: "pink", g: ["XXX", "..X"] },
    { c: "pink", g: ["XXXX"] },
    { c: "pink", g: ["XXX", "X..", "X.."] },
    { c: "pink", g: ["X.", "XX"], confirmed: false },
    { c: "pink", g: ["XX", ".X", ".X"], confirmed: false }
  ];

  /** 정의 하나를 실제 조각으로 만든다. h 칸은 칸마다 독립적으로 뽑는다. */
  function make(def, hChance) {
    var cells = [];
    for (var r = 0; r < def.g.length; r++) {
      for (var c = 0; c < def.g[r].length; c++) {
        if (def.g[r][c] === "X") {
          cells.push({ r: r, c: c, h: Math.random() < hChance });
        }
      }
    }
    var cols = 0;
    for (var i = 0; i < def.g.length; i++) cols = Math.max(cols, def.g[i].length);
    return {
      color: def.c,
      rows: def.g.length,
      cols: cols,
      cells: cells
    };
  }

  function random(hChance) {
    return make(DEFS[Math.floor(Math.random() * DEFS.length)], hChance);
  }

  return { DEFS: DEFS, make: make, random: random };
})();
