"""원작 영상에서 TIME BONUS! 워드아트를 알파 채널까지 잘라낸다.

banner_crop.py 와 달리 '배너 없는 깨끗한 같은 배경 프레임'이 없다 — 배너가
꺼진 직후에 이미 다음 블록이 놓여 있다. 그래서 배경 프레임을 **두 장** 쓰고
차분의 최솟값을 취한다. 어느 한 장과라도 같아 보이면 배경으로 친다.
글자는 두 장 모두와 다르므로 살아남는다.

    26.60  TIME BONUS! 가 최대 크기로 떠 있다 (PERFECT! 아래)
    27.00  배너는 꺼졌으나 블록이 새로 놓여 있다
    27.30  줄이 터져 파편이 날린다 (27.00 과 겹치는 오염이 없다)
"""
import subprocess, tempfile, os
import numpy as np
from scipy import ndimage
from PIL import Image, ImageFilter

VIDEO = r"C:\Users\nutel\OneDrive\Desktop\dev\hgame\KakaoTalk_20260817_025744434.mp4"
OUT = r"C:\Users\nutel\OneDrive\Desktop\dev\block-game\assets\banner_timebonus.png"
BOX = (40, 630, 1040, 790)          # 넉넉히 자르고 마지막에 getbbox 로 조인다
TOP = 22                            # BOX 안에서 글자가 시작되는 y (실측)
T_ON = 26.60
T_OFF = [27.00, 27.30, 27.70, 28.20]

tmp = tempfile.mkdtemp()


def frame(t):
    p = os.path.join(tmp, "f%.2f.png" % t)
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-ss", str(t),
                    "-i", VIDEO, "-frames:v", "1", p], check=True)
    return Image.open(p).convert("RGB").crop(BOX)


on = frame(T_ON)
a = np.asarray(on).astype(int)

d = None
for t in T_OFF:
    e = np.abs(a - np.asarray(frame(t)).astype(int)).max(axis=2)
    d = e if d is None else np.minimum(d, e)

# 20 이하 배경 / 60 이상 완전 불투명으로 램프 (banner_crop.py 와 같은 기준)
alpha = np.clip((d - 20) * 255 / 40, 0, 255).astype(np.uint8)

# ON 프레임에만 있던 '드래그 중인 블록'이 얼룩으로 남는다. 두 번에 나눠 지운다.
alpha[:TOP, :] = 0                       # 글자보다 위는 전부 배경이다
mask = alpha > 60
lab, n = ndimage.label(mask)
size = ndimage.sum(mask, lab, range(1, n + 1))
alpha[np.isin(lab, [i for i in range(1, n + 1) if size[i - 1] < 2000])] = 0
alpha[ndimage.binary_fill_holes(alpha > 60) & (alpha <= 60)] = 255   # 글자 속 구멍

alpha = Image.fromarray(alpha).filter(ImageFilter.MaxFilter(3)) \
                              .filter(ImageFilter.GaussianBlur(0.6))

on.putalpha(alpha)
on = on.crop(on.getbbox())
on.save(OUT)
print(OUT, on.size)
