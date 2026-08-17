"""원작 영상에서 NICE! / PERFECT! 워드아트를 알파 채널까지 잘라낸다.

배너는 항상 보드 위쪽 빈 칸들 위에 뜬다. 그래서 같은 구간의 '배너 없는 프레임'과
차분하면 배경(빈 칸 + 격자선)이 지워지고 글자만 남는다.
"""
import subprocess, tempfile, os
from PIL import Image, ImageChops, ImageFilter

VIDEO = r"C:\Users\nutel\OneDrive\Desktop\dev\hgame\KakaoTalk_20260817_025744434.mp4"
OUT = r"C:\Users\nutel\OneDrive\Desktop\dev\block-game\assets"

# (파일명, 배너가 최대 크기로 떠 있는 시각, 같은 구간의 배너 없는 시각, 크롭 박스)
JOBS = [
    ("banner_perfect.png", 8.200, 9.600, (140, 386, 942, 541)),
    ("banner_nice.png",    9.033, 9.600, (330, 400, 752, 523)),
]

tmp = tempfile.mkdtemp()


def frame(t):
    p = os.path.join(tmp, "f%.3f.png" % t)
    if not os.path.exists(p):
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(t),
                        "-i", VIDEO, "-frames:v", "1", p], check=True)
    return Image.open(p).convert("RGB")


for name, t_on, t_off, box in JOBS:
    fg = frame(t_on).crop(box)
    bg = frame(t_off).crop(box)

    # 차분 → 알파. 20 이하는 배경, 60 이상은 완전 불투명으로 램프
    d = ImageChops.difference(fg, bg).convert("L")
    a = d.point(lambda v: 0 if v < 20 else min(255, round((v - 20) * 255 / 40)))
    a = a.filter(ImageFilter.MaxFilter(3)).filter(ImageFilter.GaussianBlur(0.6))

    fg.putalpha(a)
    fg.save(os.path.join(OUT, name))
    print(name, fg.size)
