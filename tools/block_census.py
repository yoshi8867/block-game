"""영상에서 트레이에 등장한 블록을 세어 35종이 균등하게 나오는지 본다.

트레이 세 칸을 프레임마다 읽어 (모양, 색) 을 판별하고, 칸의 내용이 바뀔 때마다
새 블록 하나로 센다. 판정 기준은 layout.css 의 실측 비율 그대로다.

한계: 같은 칸에 같은 모양이 **연달아** 나오면 한 번으로 센다. 드래그했다 되돌린
블록을 새것으로 세지 않으려고 그렇게 했다 (안 그러면 붙들고 고민하는 시간이 긴
큰 블록만 몇 배로 부풀려진다). 35종이면 연속 중복은 3% 정도라 치우침은 없다.
표본이 작으므로 결론은 신중히 볼 것.
"""
import subprocess, os, re, sys
from collections import Counter
import numpy as np
from scipy import ndimage

HGAME = r"C:\Users\nutel\OneDrive\Desktop\dev\hgame"
BLOCKS_JS = os.path.join(os.path.dirname(__file__), "..", "js", "blocks.js")
VIDEOS = ["KakaoTalk_20260817_025744434.mp4", "KakaoTalk_20260817_032722265.mp4"]
FPS = int(next((a.split("=")[1] for a in sys.argv if a.startswith("--fps=")), 5))

W, H = 1080, 2340
SLOT_X = [0.1028, 0.3815, 0.6602]
SLOT_TOP, SLOT_W, SLOT_H = 0.6056, 0.2444, 0.1154
TRAY_SCALE = 0.54
CELL = 101 * TRAY_SCALE            # 54.54 px
PITCH = 108.43 * TRAY_SCALE        # 58.55 px

CROP_X, CROP_W = 100, 890
CROP_Y, CROP_H = 1408, 288

# ── blocks.js 의 35종 정의를 그대로 읽어 온다 ──────────────────
DEFS = []
for m in re.finditer(r'\{\s*c:\s*"(\w+)",\s*g:\s*\[([^\]]*)\]', open(BLOCKS_JS, encoding="utf-8").read()):
    rows = re.findall(r'"([X.]+)"', m.group(2))
    DEFS.append((m.group(1), tuple(rows)))
assert len(DEFS) == 35, len(DEFS)
BY_KEY = {(c, g): i for i, (c, g) in enumerate(DEFS)}

# ── 색 기준: assets/cell_*.png 의 평균 색 ──────────────────────
def ref_colors():
    from PIL import Image
    out = {}
    d = os.path.join(os.path.dirname(__file__), "..", "assets")
    for name in ("purple", "cyan", "yellow", "pink"):
        a = np.asarray(Image.open(os.path.join(d, "cell_%s.png" % name)).convert("RGBA"))
        m = a[:, :, 3] > 200
        out[name] = a[:, :, :3][m].mean(axis=0)
    return out


REF = ref_colors()


def read_shape(img, sx):
    """슬롯 하나에서 (모양행들, 색) 을 읽는다. 비었으면 None."""
    x0 = int(round(sx * W)) - CROP_X
    y0 = int(round(SLOT_TOP * H)) - CROP_Y
    s = img[max(0, y0): y0 + int(SLOT_H * H), max(0, x0): x0 + int(SLOT_W * W)]
    if s.size == 0:
        return None
    mx = s.max(axis=2).astype(int)
    mn = s.min(axis=2).astype(int)
    tile = (mx > 110) & (mx - mn > mx * 0.22)     # 밝고 채도 있는 픽셀 = 타일
    # 슬롯은 모서리가 둥글어서 사각으로 자르면 네 귀퉁이에 별 배경이 딸려 온다.
    # 타일은 슬롯 안쪽에만 있으므로 테두리에 닿는 덩어리는 전부 버린다.
    lab, n = ndimage.label(tile)
    edge = set(lab[0]) | set(lab[-1]) | set(lab[:, 0]) | set(lab[:, -1])
    edge.discard(0)
    if edge:
        tile &= ~np.isin(lab, list(edge))
    if tile.sum() < 0.25 * CELL * CELL:
        return None
    ys, xs = np.where(tile)
    top, bot, left, right = ys.min(), ys.max(), xs.min(), xs.max()
    cols = int(round((right - left + 1 - CELL) / PITCH)) + 1
    rows = int(round((bot - top + 1 - CELL) / PITCH)) + 1
    if not (1 <= rows <= 4 and 1 <= cols <= 4):
        return None
    g, filled = [], []
    for r in range(rows):
        line = ""
        for c in range(cols):
            cy = int(top + r * PITCH + CELL / 2)
            cx = int(left + c * PITCH + CELL / 2)
            k = int(CELL * 0.22)
            patch = tile[cy - k: cy + k, cx - k: cx + k]
            on = patch.mean() > 0.6
            line += "X" if on else "."
            if on:
                filled.append(s[cy - k: cy + k, cx - k: cx + k].reshape(-1, 3))
        g.append(line)
    if not filled or not any("X" in r for r in g):
        return None
    # 가장자리 줄이 비면 모양이 잘못 잡힌 것
    if g[0].count("X") == 0 or g[-1].count("X") == 0:
        return None
    if all(r[0] == "." for r in g) or all(r[-1] == "." for r in g):
        return None
    px = np.concatenate(filled).astype(float)
    px = px[px.max(axis=1) > 120]                # 흰 'h' 표시는 빼고 본다
    if len(px) < 50:
        return None
    mean = px.mean(axis=0)
    color = min(REF, key=lambda n: np.linalg.norm(REF[n] - mean))
    return tuple(g), color


def frames(path):
    cmd = ["ffmpeg", "-v", "error", "-i", path, "-vf",
           "fps=%d,crop=%d:%d:%d:%d" % (FPS, CROP_W, CROP_H, CROP_X, CROP_Y),
           "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, bufsize=CROP_W * CROP_H * 3)
    n = CROP_W * CROP_H * 3
    while True:
        buf = p.stdout.read(n)
        if len(buf) < n:
            break
        yield np.frombuffer(buf, np.uint8).reshape(CROP_H, CROP_W, 3)
    p.stdout.close()
    p.wait()


LIST = "--list" in sys.argv
HOLD = 2                        # 이만큼 연속으로 같아야 '자리잡은 블록'으로 본다

seen = Counter()
unknown = Counter()
per_slot = Counter()
log = []
for v in VIDEOS:
    last = [None, None, None]
    hold = [0, 0, 0]
    held = [None, None, None]      # 그 칸에 마지막으로 자리잡았던 블록
    cnt = 0
    fi = 0
    for img in frames(os.path.join(HGAME, v)):
        fi += 1
        for i, sx in enumerate(SLOT_X):
            cur = read_shape(img, sx)
            if cur == last[i]:
                hold[i] += 1
                # 직전에 자리잡았던 것과 **다른** 블록일 때만 새 블록으로 센다.
                # 드래그했다 되돌린 블록이 다시 보이는 걸 새것으로 세면 안 된다
                # (큰 블록일수록 오래 붙들고 있어 그쪽만 부풀려진다).
                if hold[i] == HOLD and cur is not None and cur != held[i]:
                    held[i] = cur
                    key = (cur[1], cur[0])
                    if key in BY_KEY:
                        seen[BY_KEY[key]] += 1
                    else:
                        unknown[key] += 1
                    per_slot[i] += 1
                    cnt += 1
                    log.append((v[-9:-4], fi / FPS, i, cur[1], "/".join(cur[0])))
            else:
                last[i] = cur
                hold[i] = 0
    print("%s  →  블록 %d 개" % (v, cnt))

if LIST:
    for row in log:
        print("   %s %6.1fs 슬롯%d  %-7s %s" % row)
print("슬롯별 %s" % dict(per_slot))

print("\n판별 실패(정의에 없는 모양·색) %d 종 %d 개" % (len(unknown), sum(unknown.values())))
for k, n in unknown.most_common(10):
    print("   %-8s %-22s %d" % (k[0], "/".join(k[1]), n))

print("\n35종 출현 횟수 (총 %d)" % sum(seen.values()))
for i, (c, g) in enumerate(DEFS):
    print("  %2d  %-7s %-14s %s" % (i, c, "/".join(g), "■" * seen[i] if seen[i] else "-"))

n = sum(seen.values())
if n:
    obs = np.array([seen[i] for i in range(35)])
    exp = n / 35
    chi = ((obs - exp) ** 2 / exp).sum()
    print("\n총 %d개, 종당 기대 %.1f개, 실제 %d~%d개" % (n, exp, obs.min(), obs.max()))
    print("카이제곱 %.1f (자유도 34, 균등이면 34 근처, 5%% 유의 임계 48.6)" % chi)
    byc = Counter()
    for i, (c, _) in enumerate(DEFS):
        byc[c] += seen[i]
    print("색깔별:", dict(byc), " (정의 개수 purple 9 / cyan 9 / yellow 9 / pink 8)")
