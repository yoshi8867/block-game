"""원작 프레임에서 8x8 격자를 잘라 assets/board.png 를 만든다.

격자 외곽선은 셀 영역 밖으로 4.5px 나간다(실측). 그래서 각 변 10px 패딩을 두고
자르되, 외곽선 바깥의 배경은 알파 0으로 잘라낸다 — 안 그러면 패딩 영역이
반투명한 사각 링처럼 보인다.
"""
from PIL import Image, ImageDraw

SRC = r"C:\Users\nutel\OneDrive\Desktop\dev\hgame\docs\bg_source.png"
OUT = r"C:\Users\nutel\OneDrive\Desktop\dev\block-game\assets\board.png"

CELL_L, CELL_T = 111, 416      # 셀 영역 좌상단 (원본 프레임 좌표)
CELL_SIZE = 860                # 셀 영역 한 변
PAD = 10                       # 크롭 여유
OVER = 4.5                     # 외곽선이 셀 영역 밖으로 나가는 양
RADIUS = 25                    # 외곽 모서리 반경
SS = 4                         # 안티에일리어싱용 슈퍼샘플링

size = CELL_SIZE + PAD * 2
img = Image.open(SRC).convert("RGBA").crop(
    (CELL_L - PAD, CELL_T - PAD, CELL_L + CELL_SIZE + PAD, CELL_T + CELL_SIZE + PAD))

lo = PAD - OVER
hi = size - (PAD - OVER)
mask = Image.new("L", (size * SS, size * SS), 0)
ImageDraw.Draw(mask).rounded_rectangle(
    (lo * SS, lo * SS, hi * SS - 1, hi * SS - 1), radius=RADIUS * SS, fill=255)
img.putalpha(mask.resize((size, size), Image.LANCZOS))
img.save(OUT)
print("saved", OUT, img.size, "silhouette", lo, "..", hi)
