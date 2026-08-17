"""intro.mp3 의 '띠' 소리 시작 시각을 찾는다.

카운트다운 텍스트(3·2·1·GO!)를 소리에 맞추려고 만든 것. 결과는 todo.md 에 적어 둔다.
"""
import subprocess, numpy as np, os

SRC = os.path.join(os.path.dirname(__file__), "..", "audio", "intro.mp3")
SR = 8000

raw = subprocess.run(
    ["ffmpeg", "-v", "error", "-i", SRC, "-ac", "1", "-ar", str(SR),
     "-f", "s16le", "-"], check=True, capture_output=True).stdout
x = np.frombuffer(raw, dtype="<i2").astype(float) / 32768

win = SR // 100                                   # 10ms
n = len(x) // win
env = np.abs(x[: n * win].reshape(n, win)).max(axis=1)

thr = env.max() * 0.25
on = (env > thr) & (np.r_[False, env[:-1] <= thr])  # 문턱을 위로 넘는 순간

for i in np.flatnonzero(on):
    # 소리가 끊기는 지점까지가 그 '띠' 의 길이
    j = i
    while j < n and env[j] > thr:
        j += 1
    print("%6.3f s  길이 %5.3f s  피크 %.2f" % (i / 100, (j - i) / 100, env[i:j].max()))
print("전체 %.3f s" % (len(x) / SR))
