"""사용자가 준 GAME OVER 워드아트에서 체커보드 배경을 지우고 알파를 만든다.

받은 PNG 는 알파가 전부 255 이고 투명 체커무늬(#D5D5D5 / #FFFFFF)가 픽셀로
박혀 있다. 흰 체커는 글자 광택(#FFFFFF)과 색이 같아서 색만으로는 못 가른다.

가르는 기준: **체커 덩어리에는 회색 칸(#D5D5D5)이 절반쯤 섞여 있고, 광택은
순백뿐**이다. 그래서 밝고 무채색인 덩어리마다 회색 비율을 재서 판별한다.
O·R 안쪽 구멍처럼 테두리와 안 이어진 체커도 이 방법이면 같이 잡힌다.
"""
from PIL import Image, ImageFilter
import numpy as np
from scipy import ndimage

SRC = r"C:\Users\nutel\Downloads\Gemini_Generated_Image_pyxrz7pyxrz7pyxr.png"
OUT = r"C:\Users\nutel\OneDrive\Desktop\dev\block-game\assets\gameover.png"
WIDTH = 900             # 표시 폭 640px @1080. 고DPI 폰에서도 이 정도면 충분.

im = Image.open(SRC).convert("RGB")
a = np.asarray(im).astype(int)
r, g, b = a[:, :, 0], a[:, :, 1], a[:, :, 2]

# 밝고 무채색 = 체커 후보 (글자 광택도 여기 걸리지만 아래에서 걸러진다)
mx, mn = a.max(axis=2), a.min(axis=2)
cand = (mx > 170) & (mx - mn < 26)

gray = cand & (mx >= 195) & (mx <= 232)      # 체커의 회색 칸

lab, n = ndimage.label(cand)
size = ndimage.sum(cand, lab, range(1, n + 1))
gsize = ndimage.sum(gray, lab, range(1, n + 1))
frac = np.divide(gsize, size, out=np.zeros_like(gsize), where=size > 0)

edge = set(lab[0, :]) | set(lab[-1, :]) | set(lab[:, 0]) | set(lab[:, -1])
edge.discard(0)
ids = [i for i in range(1, n + 1) if frac[i - 1] > 0.25 or i in edge]
bg = np.isin(lab, ids)

# 검은 외곽선과 체커 사이의 회색 경계선이 후광으로 남는다. 한 겹 넓혀 먹인다.
bg = ndimage.binary_dilation(bg, iterations=1)

alpha = Image.fromarray(np.where(bg, 0, 255).astype(np.uint8))
alpha = alpha.filter(ImageFilter.GaussianBlur(0.8))

im.putalpha(alpha)
im = im.crop(im.getbbox())
im = im.resize((WIDTH, round(im.height * WIDTH / im.width)), Image.LANCZOS)
im.save(OUT)
print("saved", OUT, im.size, "(배경 덩어리 %d개 제거)" % len(ids))
