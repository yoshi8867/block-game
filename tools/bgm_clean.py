"""BGM 루프를 효과음 없이 다시 만든다.

원래 bgm_loop.wav 는 영상에서 손으로 자른 한 바퀴라 NICE!/PERFECT!/블록 놓는
소리가 섞여 있었다. 그런데 BGM 은 **25.65초마다 똑같이 반복**되고, 두 영상에
합쳐 여덟 바퀴가 들어 있다. 같은 위상의 여덟 조각을 겹쳐 놓고 매 순간
**가장 조용한 조각**을 고르면 효과음만 빠진다 (효과음은 BGM 위에 더해진 것이므로
효과음이 없는 조각이 언제나 가장 작다).

절차
  1. 3초짜리 기준 조각으로 상호상관을 걸어 각 영상에서 루프 시작점을 찾는다
  2. 여덟 조각을 표본 단위까지 정렬한다 (녹화 클럭이 조금씩 흔들린다)
  3. 23ms 창마다 에너지를 재서, 최솟값의 1.25배 안에 드는 조각을 '깨끗하다'고 본다
  4. 왼쪽부터 훑으며 '지금부터 가장 오래 깨끗한' 조각을 골라 이어 붙인다.
     이음매는 46ms 크로스페이드 — 양쪽 다 깨끗한 지점에서만 갈아탄다
  5. 한 주기를 정확히 떠냈으므로 끝과 처음은 저절로 이어진다
"""
import subprocess, os, wave
import numpy as np

HGAME = r"C:\Users\nutel\OneDrive\Desktop\dev\hgame"
OUT = r"C:\Users\nutel\OneDrive\Desktop\dev\block-game\audio\bgm_loop.mp3"
TMP = os.path.join(os.environ.get("TEMP", "."), "bgm_clean")

SR = 44100
# 루프 주기. 처음엔 25.650 으로 잡았는데, 조각들의 정렬 보정값이 한 바퀴마다
# 98 표본씩 밀리는 것을 보고 25.65222 초(1131263 표본)로 다듬었다.
# v1 의 세 구간(30.000→55.652→81.305)이 1 표본 안에서 이 값에 일치한다.
# 파일 길이가 곧 루프 길이이므로 이 값이 틀리면 이음매에서 딸꾹거린다.
PERIOD_SAMPLES = 1131263
HOP = 1024                         # 23ms
FADE = 2048                        # 46ms 크로스페이드
CLEAN = 1.25                       # 최소 에너지의 몇 배까지 깨끗하다고 볼지

# (영상파일, 첫 루프 시작 시각) — period.py 의 상호상관으로 찾은 값
SOURCES = [
    ("KakaoTalk_20260817_025744434.mp4", 4.356),
    ("KakaoTalk_20260817_032722265.mp4", 7.088),
]


def audio(name):
    os.makedirs(TMP, exist_ok=True)
    p = os.path.join(TMP, name + ".wav")
    if not os.path.exists(p):
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", os.path.join(HGAME, name),
                        "-vn", "-ac", "1", "-ar", str(SR), "-c:a", "pcm_s16le", p],
                       check=True)
    with wave.open(p) as w:
        return np.frombuffer(w.readframes(w.getnframes()), "<i2").astype(np.float64) / 32768


def best_lag(a, b, span):
    """b 를 a 에 맞추려면 몇 표본 밀어야 하는지 (|lag| <= span)"""
    n = 1 << int(np.ceil(np.log2(len(a) + len(b))))
    c = np.fft.irfft(np.fft.rfft(a, n) * np.conj(np.fft.rfft(b, n)), n)
    c = np.concatenate([c[-span:], c[:span + 1]])
    return int(np.argmax(c)) - span


P = PERIOD_SAMPLES
tracks = [(audio(f), int(round(t0 * SR))) for f, t0 in SOURCES]

# ── 1) 조각 모으기 ────────────────────────────────────────────
raw = []
for sig, t0 in tracks:
    k = 0
    while t0 + k * P < len(sig) - SR:          # 1초도 안 남으면 버린다
        raw.append((sig, t0 + k * P))
        k += 1

anchor = None
pieces = []
for sig, s in raw:
    seg = np.zeros(P)
    have = min(P, len(sig) - s)
    seg[:have] = sig[s: s + have]
    if anchor is None:
        anchor = seg
        lag = 0
    else:
        lag = best_lag(anchor, seg, SR // 20)   # ±50ms
        s2 = s - lag
        have = min(P, len(sig) - s2)
        seg = np.zeros(P)
        seg[:have] = sig[max(0, s2): max(0, s2) + have]
    ok = np.zeros(P, bool)
    ok[:have] = True
    pieces.append((seg, ok, lag, have))
    print("조각 %2d  시작 %8.3f s  보정 %+4d 표본  길이 %6.3f s"
          % (len(pieces) - 1, s / SR, lag, have / SR))

X = np.array([p[0] for p in pieces])
VALID = np.array([p[1] for p in pieces])

# ── 2) 창마다 에너지 → 깨끗한 조각 표시 ────────────────────────
nw = P // HOP
E = np.empty((len(X), nw))
V = np.empty((len(X), nw), bool)
for i in range(len(X)):
    E[i] = np.sqrt((X[i, :nw * HOP].reshape(nw, HOP) ** 2).mean(axis=1))
    V[i] = VALID[i, :nw * HOP].reshape(nw, HOP).all(axis=1)
E[~V] = np.inf

floor = np.maximum(E.min(axis=0), 1e-5)   # 완전 무음 창에서 0 나눗셈 방지
clean = E <= floor * CLEAN + 1e-6
print("창 %d 개, 창마다 깨끗한 조각 평균 %.2f 개, 최소 %d 개"
      % (nw, clean.sum(axis=0).mean(), clean.sum(axis=0).min()))

# ── 3) 왼쪽부터 '가장 오래 버티는' 조각을 이어 붙인다 ───────────
def run_from(i, w):
    j = w
    while j < nw and clean[i, j]:
        j += 1
    return j


def valid_to(i, w):
    j = w
    while j < nw and V[i, j]:
        j += 1
    return j


MINW = 4 * FADE // HOP              # 이음매가 겹칠 만큼 짧은 토막은 만들지 않는다

# 루프 경계(파일 끝 → 처음)에는 크로스페이드를 걸 수 없다. 그래서 **처음과 끝을
# 같은 조각**으로 덮어 경계를 아예 이음매가 아니게 만든다. 양쪽 끝 MINW 창이
# 모두 깨끗한 조각 중 앞쪽으로 가장 오래 버티는 것을 고른다.
def wrap_cost(i):
    w = np.concatenate([E[i, -MINW:], E[i, :MINW]])
    return np.inf if not np.isfinite(w).all() else w.sum()


head = int(min(range(len(X)), key=wrap_cost))
tail = nw
while tail > 0 and clean[head, tail - 1]:
    tail -= 1
tail = max(tail, nw - nw // 4)      # 꼬리를 너무 길게 잡아 통째로 삼키지 않게
print("루프 경계 담당 조각 %d — 처음과 끝(%.2fs~)을 같은 조각으로 덮는다"
      % (head, tail * HOP / SR))

plan, w = [], 0
while w < nw:
    if w == 0:
        end = min(tail, max(run_from(head, 0), MINW))
        plan.append((head, 0, end))
        w = end
        continue
    if w >= tail:
        plan.append((head, w, nw))
        break
    cand = [i for i in range(len(X)) if clean[i, w]] or [int(np.argmin(E[:, w]))]
    i = max(cand, key=lambda i: run_from(i, w))
    # 짧은 토막은 피하되, 그 조각이 실제로 있는 데까지만 늘린다
    limit = tail
    end = min(valid_to(i, w), limit, max(run_from(i, w), w + MINW))
    if limit - end < MINW:          # 꼬리 토막은 앞 구간에 붙인다
        end = limit
    plan.append((i, w, end))
    w = end
print("이음매 %d 개:" % (len(plan) - 1),
      " ".join("%d@%.2fs" % (i, w * HOP / SR) for i, w, _ in plan))

out = np.zeros(P)
win = np.zeros(P)
for i, w0, w1 in plan:
    a, b = w0 * HOP, min(w1 * HOP, P)
    lo, hi = max(0, a - FADE), min(P, b + FADE)
    env = np.ones(hi - lo)
    pre, post = a - lo, hi - b           # 앞뒤로 겹치는 길이 (보통 FADE)
    if pre:
        env[: pre * 2] = np.linspace(0, 1, pre * 2)
    if post:
        env[-post * 2:] = np.minimum(env[-post * 2:], np.linspace(1, 0, post * 2))
    out[lo:hi] += X[i, lo:hi] * env
    win[lo:hi] += env
out /= np.maximum(win, 1e-9)

# 원본 음량 유지 (조각들의 중앙값 RMS 에 맞춘다)
ref_rms = float(np.median([np.sqrt((X[i] ** 2).mean()) for i in range(len(X))]))
out *= ref_rms / np.sqrt((out ** 2).mean())
peak = np.abs(out).max()
if peak > 0.99:
    out *= 0.99 / peak

wav = os.path.join(TMP, "clean.wav")
with wave.open(wav, "w") as w:
    w.setnchannels(1)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((np.clip(out, -1, 1) * 32767).astype("<i2").tobytes())

subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", wav,
                "-codec:a", "libmp3lame", "-q:a", "3", OUT], check=True)
print("\n%s  %.5f 초" % (OUT, P / SR))

# ── 검증 ──────────────────────────────────────────────────────
chosen = np.empty(nw)
for i, w0, w1 in plan:
    chosen[w0:w1] = E[i, w0:w1]
dirty = (chosen > floor * CLEAN + 1e-6).sum()
med = np.median(floor)
print("깨끗한 조각을 못 찾은 창: %d / %d" % (dirty, nw))
peaks = [E[i][V[i]].max() / med for i in range(len(X))]
print("창 에너지 최대/중앙값  원본조각들 %.2f~%.2f배 → 결과 %.2f배"
      % (min(peaks), max(peaks), chosen.max() / med))
print("전체 피크 %.3f" % np.abs(out).max())
print("창 에너지 / 그 창의 최솟값  (1.00 이면 효과음 없음)")
for i in range(len(X)):
    r = (E[i] / floor)[V[i]]
    print("   조각 %d  중앙값 %.3f   1.25배 초과 창 %4d / %4d"
          % (i, np.median(r), (r > 1.25).sum(), len(r)))
r = chosen / floor
print("   결과     중앙값 %.3f   1.25배 초과 창 %4d / %4d"
      % (np.median(r), (r > 1.25).sum(), nw))
