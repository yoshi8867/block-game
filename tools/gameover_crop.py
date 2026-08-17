"""원작 영상에서 GAME OVER 워드아트를 알파까지 잘라낸다.

원작에서 이 글자는 **타일보다 아래**에 깔린다(글자가 블록에 가려진다).
그래서 글자가 빈 칸 위에 오는 부분만 온전히 보인다. 마침 마지막 판의 배치가
글자 대부분을 비워 줬다.

t=103.60 에 뜨고 그 뒤로 안 변한다. 직전 프레임(103.50)을 배경으로 차분한다.
"""
import subprocess, tempfile, os
from PIL import Image, ImageChops, ImageFilter

VIDEO = r"C:\Users\nutel\OneDrive\Desktop\dev\hgame\KakaoTalk_20260817_025744434.mp4"
OUT = r"C:\Users\nutel\OneDrive\Desktop\dev\block-game\assets\gameover.png"
BOX = (120, 1080, 960, 1240)

tmp = tempfile.mkdtemp()


def frame(t):
    p = os.path.join(tmp, "f%.2f.png" % t)
    if not os.path.exists(p):
        subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(t),
                        "-i", VIDEO, "-frames:v", "1", p], check=True)
    return Image.open(p).convert("RGB")


fg = frame(106.55).crop(BOX)
bg = frame(103.50).crop(BOX)

# 경고 비네트가 두 프레임 사이에 조금 달라져 있다(휘도 5 정도). 그보다 높게 자른다.
d = ImageChops.difference(fg, bg)
r, g, b = d.split()
m = ImageChops.lighter(ImageChops.lighter(r, g), b)
a = m.point(lambda v: 0 if v < 30 else min(255, round((v - 30) * 255 / 35)))
a = a.filter(ImageFilter.MedianFilter(3)).filter(ImageFilter.GaussianBlur(0.6))

fg.putalpha(a)
bb = fg.getbbox()
fg = fg.crop(bb)
fg.save(OUT)
print(OUT, fg.size, "원본 위치 x %d..%d  y %d..%d" %
      (BOX[0] + bb[0], BOX[0] + bb[2], BOX[1] + bb[1], BOX[1] + bb[3]))
