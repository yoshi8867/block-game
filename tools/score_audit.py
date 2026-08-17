"""원작 영상의 점수 증가분을 전부 채점 공식으로 분해해 본다.

    획득점수 = 800 x 완성한 줄 + 100 x (완성한 줄의 h 칸) + 15 x 내려놓은 칸

점수는 두 영상에서 점수 알약이 바뀔 때마다 잘라내 눈으로 읽은 값이다
(scratchpad/pills.py 가 대조표 이미지를 만든다). 하나라도 분해가 안 되면
놓친 규칙이 있다는 뜻이다.

같이 확인하는 것
  - TIME BONUS! 가 뜨는 시각과 그때의 점수
  - 그 순간 게이지(남은 시간)가 늘어나는지  → 시간을 주는 보너스인지 판별
"""
import subprocess, os
import numpy as np

HGAME = r"C:\Users\nutel\OneDrive\Desktop\dev\hgame"
W, H = 1080, 2340

# 점수 알약을 눈으로 읽은 값 (변할 때마다 한 번씩)
V1 = [0, 60, 135, 210, 1355, 2215, 2260, 2320, 3295, 3355, 4645, 4780, 4840,
      5855, 5915, 6050, 6895, 7840, 9000, 9060, 9990, 11050, 11125, 12115,
      12175, 12265, 13225, 13300, 14345, 14405, 14465, 14525, 15470, 15500,
      16330, 16390, 16480, 16510, 16570, 17415, 18375, 19335, 19395, 19470,
      21460, 22420, 22480, 22495, 23455, 23530, 24620, 25680, 25815, 26775,
      27835, 27895, 28855, 28945, 29005, 29050, 29110, 30170, 30245, 32105,
      32165, 32225, 33355, 35375, 35435, 35495]
V2 = [0, 60, 120, 180, 225, 1270, 1345, 1405, 1465, 1525, 1615, 1675, 2690,
      3550, 4410, 5540, 5600, 6515, 6650, 6725, 6770, 6860, 8920, 9880, 10840,
      10900, 12075, 13150, 13240, 13375, 15335, 15395, 15440, 16285, 16315,
      17290, 17350, 17410, 18400, 19290, 19350, 20210, 20345, 20405, 21550,
      21610, 21685, 22915, 22990, 23950, 24010, 24070, 26115, 27075, 27135,
      27195, 27255, 28200, 28230, 28275, 29595, 30625, 31785, 32990, 33935]

LINE, HCELL, CELL = 800, 100, 15


def decompose(d):
    """(줄, h, 칸) 후보들. 칸은 1~9, h 는 줄당 최대 8칸."""
    out = []
    for lines in range(0, 5):
        for cells in range(1, 10):
            rest = d - LINE * lines - CELL * cells
            if rest < 0 or rest % HCELL:
                continue
            h = rest // HCELL
            if h > 8 * lines:            # 지운 줄에 없는 h 는 셀 수 없다
                continue
            out.append((lines, h, cells))
    return out


print("점수 증가분 분해 (줄 x800 + h x100 + 칸 x15)")
bad = []
for name, seq in (("v1", V1), ("v2", V2)):
    for a, b in zip(seq, seq[1:]):
        d = b - a
        cand = decompose(d)
        if not cand:
            bad.append((name, a, b, d))
        tag = "" if cand else "   <-- 분해 불가"
        if not cand or len(cand) > 3:
            print("  %s %6d -> %-6d  +%-5d  %s%s"
                  % (name, a, b, d, cand[:3], tag))
print("분해 불가 %d 건" % len(bad))

n = len(V1) + len(V2) - 2
uniq = sum(1 for name, seq in (("v1", V1), ("v2", V2))
           for a, b in zip(seq, seq[1:]) if len(decompose(b - a)) == 1)
print("증가분 %d 건 중 해석이 하나뿐인 것 %d 건" % (n, uniq))

# ── TIME BONUS! 와 게이지 ──────────────────────────────────────
TB_Y0, TB_Y1 = 640, 790          # TIME BONUS! 워드아트가 있는 띠
G_X0, G_X1, G_Y = 752, 1050, 145  # 게이지 (69.63%~97.22%, 세로 중심 6.2%)


def scan_gauge_and_banner(video, fps=5):
    cmd = ["ffmpeg", "-v", "error", "-i", os.path.join(HGAME, video),
           "-vf", "fps=%d" % fps, "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=W * H * 3)
    n = W * H * 3
    i = 0
    while True:
        buf = p.stdout.read(n)
        if len(buf) < n:
            break
        img = np.frombuffer(buf, np.uint8).reshape(H, W, 3)
        band = img[TB_Y0:TB_Y1].astype(int)
        mx, mn = band.max(axis=2), band.min(axis=2)
        tb = ((mx > 200) & (mn > 170)).mean()        # 워드아트의 흰 테두리
        row = img[G_Y, G_X0:G_X1].astype(int)
        lit = (row.max(axis=1) > 120) & (row[:, 0] > 90)
        fill = (np.flatnonzero(lit).max() + 1) / (G_X1 - G_X0) if lit.any() else 0
        yield i / fps, tb, fill
        i += 1
    p.stdout.close()
    p.wait()


print("\nTIME BONUS! 순간의 게이지 변화")
for v in ("KakaoTalk_20260817_025744434.mp4", "KakaoTalk_20260817_032722265.mp4"):
    hist = list(scan_gauge_and_banner(v))
    thr = np.quantile([h[1] for h in hist], 0.98) * 0.6 + 0.002
    on = [h for h in hist if h[1] > thr]
    groups = []
    for t, tb, fill in on:
        if groups and t - groups[-1][-1][0] < 1.5:
            groups[-1].append((t, tb, fill))
        else:
            groups.append([(t, tb, fill)])
    print(" %s  후보 %d 회 (문턱 %.4f)" % (v[-9:-4], len(groups), thr))
    for g in groups:
        t0, t1 = g[0][0], g[-1][0]
        before = [h[2] for h in hist if t0 - 1.6 <= h[0] < t0 - 0.2]
        after = [h[2] for h in hist if t1 + 0.2 < h[0] <= t1 + 1.6]
        if before and after:
            print("   %6.1f~%5.1fs  게이지 %.3f -> %.3f  (%+.3f)"
                  % (t0, t1, max(before), max(after), max(after) - max(before)))
