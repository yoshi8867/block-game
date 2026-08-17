"""원작 영상에서 카운트다운 3 / 2 / 1 / GO! 를 알파까지 잘라낸다.

카운트다운은 빈 보드 위에 뜬다. 배너와 같은 방식으로 '카운트다운이 끝난 직후,
아직 아무것도 안 놓인' 프레임과 차분해 배경(빈 칸 + 격자선)을 지운다.

측정 결과 각 단계는 정확히 1.0초씩이고 색이 전부 다르다.
  3   t 0.0~0.5(녹화 시작 전부터)  주황  #F9AB2F
  2   t 0.53~1.50                청록  #24D3BE
  1   t 1.53~2.50                하늘  #48BAFB
  GO! t 2.53~3.50                시안  #32C4E5
"""
import subprocess, tempfile, os
from PIL import Image, ImageChops, ImageFilter

VIDEO = r"C:\Users\nutel\OneDrive\Desktop\dev\hgame\KakaoTalk_20260817_025744434.mp4"
OUT = r"C:\Users\nutel\OneDrive\Desktop\dev\block-game\assets"
T_OFF = 3.60                       # 카운트다운은 끝났고 보드는 아직 빈 시각
BOX = (300, 800, 780, 1030)        # 보드 중앙, 글자가 넉넉히 들어가는 상자

JOBS = [("cd3.png", 0.30), ("cd2.png", 1.10), ("cd1.png", 2.10), ("cdgo.png", 3.10)]

tmp = tempfile.mkdtemp()


def frame(t):
    p = os.path.join(tmp, "f%.2f.png" % t)
    if not os.path.exists(p):
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(t),
                        "-i", VIDEO, "-frames:v", "1", p], check=True)
    return Image.open(p).convert("RGB")


bg = frame(T_OFF).crop(BOX)

for name, t in JOBS:
    fg = frame(t).crop(BOX)
    # 글자 뒤에 어두운 그림자가 깔려 있다. 단순 차분을 쓰면 그림자까지 따라와
    # 격자선 자국이 남는다. '배경보다 밝아진 곳'만 남긴다.
    r, g, b = ImageChops.subtract(fg, bg).split()
    m = ImageChops.lighter(ImageChops.lighter(r, g), b)
    a = m.point(lambda v: 0 if v < 30 else min(255, round((v - 30) * 255 / 40)))
    a = a.filter(ImageFilter.GaussianBlur(0.6))

    fg.putalpha(a)
    bb = fg.getbbox()
    fg = fg.crop(bb)
    fg.save(os.path.join(OUT, name))
    print("%-9s %s  원본 위치 x %d..%d y %d..%d" %
          (name, fg.size, BOX[0] + bb[0], BOX[0] + bb[2], BOX[1] + bb[1], BOX[1] + bb[3]))
