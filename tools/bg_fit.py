"""AI가 그려준 배경(736x1456)을 무대 비율(1080x2340)에 맞춘다.

가로를 채우면 세로가 204px 모자란다. 좌우를 잘라내면 하단의 도시 실루엣과
행성이 잘리므로, 대신 위쪽 하늘을 이어 붙여 늘린다.
평평한 별밭 구간을 뒤집어 얹고 이음매를 크로스페이드한다.
"""
from PIL import Image, ImageStat

SRC = r"C:\Users\nutel\OneDrive\Desktop\dev\hgame\bg_source_ai.png"
OUT = r"C:\Users\nutel\OneDrive\Desktop\dev\block-game\assets\bg.png"

W, H = 1080, 2340
BAND_TOP = 1290      # 성운이 없는 평평한 별밭 구간 (스케일 후 좌표)
FADE = 140           # 이음매 크로스페이드 길이

img = Image.open(SRC).convert("RGB")
scaled = img.resize((W, round(img.height * W / img.width)), Image.LANCZOS)
need = H - scaled.height          # 위로 이어 붙일 높이

band = scaled.crop((0, BAND_TOP, W, BAND_TOP + need + FADE)) \
             .transpose(Image.FLIP_TOP_BOTTOM)

# 위로 갈수록 어두워지는 원본 그라데이션에 맞춰 밴드 밝기를 보정한다
def mean(im):
    return ImageStat.Stat(im).mean

ref = mean(scaled.crop((0, 0, W, need + FADE)))
cur = mean(band)
band = Image.merge("RGB", [
    ch.point(lambda v, d=ref[i] - cur[i]: max(0, min(255, v + d)))
    for i, ch in enumerate(band.split())
])

canvas = Image.new("RGB", (W, H))
canvas.paste(scaled, (0, need))

# 밴드는 아래 FADE 구간에서 서서히 투명해진다
mask = Image.new("L", band.size, 255)
px = mask.load()
for y in range(need, band.height):
    a = round(255 * (1 - (y - need) / FADE))
    for x in range(W):
        px[x, y] = a
canvas.paste(band, (0, 0), mask)

canvas.save(OUT)
print("saved", OUT, canvas.size, "extended", need, "px at top")
