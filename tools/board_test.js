/* board.js 자체 검증. `node tools/board_test.js` */
const assert = require("assert");
const fs = require("fs");
eval(fs.readFileSync(__dirname + "/../js/board.js", "utf8"));

const piece = (rows, color) => ({
  color: color || "cyan", rows: rows.length, cols: rows[0].length,
  cells: rows.flatMap((s, r) =>
    [...s].map((ch, c) => (ch === "." ? null : { r, c, h: ch === "h" })).filter(Boolean))
});

Board.reset(8);

// 범위 밖 / 겹침
const bar = piece(["XXXX"]);
assert(Board.canPlace(bar, 0, 4));
assert(!Board.canPlace(bar, 0, 5), "오른쪽으로 삐져나가면 안 된다");
assert(!Board.canPlace(bar, -1, 0));
Board.place(bar, 0, 0);
assert(!Board.canPlace(bar, 0, 3), "이미 놓인 칸과 겹치면 안 된다");
assert(Board.canPlace(bar, 0, 4));

// 가로 한 줄 완성 (마지막 칸은 h)
Board.place(piece(["XXXh"]), 0, 4);
let lines = Board.fullLines();
assert.deepStrictEqual(lines, { rows: [0], cols: [] });
assert.strictEqual(Board.countH(lines), 1);
assert.strictEqual(Board.clearLines(lines).length, 8);
assert.strictEqual(Board.get(0, 0), null);

// 가로·세로 동시 완성: 교차 칸은 한 번만 지우되 두 줄 모두 카운트
Board.reset(8);
for (let c = 1; c < 8; c++) Board.place(piece(["h"]), 0, c);   // 0행 (0,0)만 비움
for (let r = 1; r < 8; r++) Board.place(piece(["X"]), r, 0);   // 0열 (0,0)만 비움
Board.place(piece(["h"]), 0, 0);                               // 교차점 채움
lines = Board.fullLines();
assert.deepStrictEqual(lines, { rows: [0], cols: [0] });
assert.strictEqual(Board.countH(lines), 8 + 1, "교차 h는 두 줄 모두에 카운트");
assert.strictEqual(Board.clearLines(lines).length, 15, "교차 칸은 한 번만 지워진다");

// 데드락 판정
Board.reset(2);
assert(Board.anyFit(piece(["XX"])));
Board.place(piece(["X"]), 0, 0);
assert(Board.anyFit(piece(["XX"])));
Board.place(piece(["X"]), 1, 0);
assert(!Board.anyFit(piece(["XX"])), "1행/2행 모두 한 칸씩 막히면 못 놓는다");

console.log("board.js OK");
