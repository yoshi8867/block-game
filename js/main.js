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

  BLOCK_CHANGE_MS: 1500    // block change 리프레시 대기
};

(function () {
  "use strict";

  Render.buildBoard(CONFIG.BOARD);
  Render.setScore(0);
  Render.setGauge(1);
})();
