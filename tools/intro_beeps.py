"""카운트다운 시작음의 '띠' 위치를 실측한다.

인자로 파일과 구간을 받는다. 기본은 새 영상(032722265)의 앞 6초 —
이쪽에 '띠 띠 띠 띠—' 네 번이 온전히 들어 있다.

    python tools/intro_beeps.py                     # 새 영상 0~6초
    python tools/intro_beeps.py ../audio/intro.mp3  # 지금 쓰는 음원
"""
import subprocess, sys, os
import numpy as np

HGAME = r"C:\Users\nutel\OneDrive\Desktop\dev\hgame"
SRC = sys.argv[1] if len(sys.argv) > 1 else \
    os.path.join(HGAME, "KakaoTalk_20260817_032722265.mp4")
DUR = float(sys.argv[2]) if len(sys.argv) > 2 else 6.0
SR = 8000

raw = subprocess.run(
    ["ffmpeg", "-v", "error", "-t", str(DUR), "-i", SRC, "-ac", "1",
     "-ar", str(SR), "-f", "s16le", "-"], check=True, capture_output=True).stdout
x = np.frombuffer(raw, dtype="<i2").astype(float) / 32768

win = SR // 200                                   # 5ms
n = len(x) // win
env = np.abs(x[: n * win].reshape(n, win)).max(axis=1)

thr = env.max() * 0.25
prev = 0.0
for i in range(1, n):
    if env[i] > thr >= env[i - 1]:
        j = i
        while j < n and env[j] > thr:
            j += 1
        t = i / 200
        print("%6.3f s  길이 %5.3f s  피크 %.2f  직전 간격 %+.3f"
              % (t, (j - i) / 200, env[i:j].max(), t - prev))
        prev = t
print("전체 %.3f s" % (len(x) / SR))
