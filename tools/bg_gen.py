"""원작 배경 색을 샘플링해 우주 배경 한 장을 생성한다. 1080x2340."""
import math, random
from PIL import Image, ImageDraw, ImageFilter

W, H = 1080, 2340
OUT = r"C:\Users\nutel\OneDrive\Desktop\dev\block-game\assets\bg.png"
random.seed(20260817)

# 원작 프레임 좌/우 끝에서 실측한 색 (y 비율, 왼쪽, 오른쪽)
STOPS = [
    (0.00, (0x6B, 0x1A, 0x7E), (0x33, 0x24, 0x6D)),
    (0.13, (0x84, 0x36, 0xA5), (0x32, 0x20, 0x70)),
    (0.21, (0x60, 0x13, 0x8C), (0x30, 0x1E, 0x6E)),
    (0.39, (0x59, 0x0F, 0x94), (0x2E, 0x1F, 0x72)),
    (0.47, (0x56, 0x0E, 0x9A), (0x2D, 0x1E, 0x74)),
    (0.64, (0x52, 0x13, 0x9D), (0x2C, 0x1F, 0x77)),
    (0.73, (0x4D, 0x10, 0x9C), (0x2E, 0x20, 0x7D)),
    (0.90, (0x3A, 0x17, 0x96), (0x29, 0x26, 0x7B)),
    (1.00, (0x33, 0x18, 0x8E), (0x25, 0x24, 0x78)),
]


def base_gradient():
    """좌우 2px x 세로 stop 수 만큼 그린 뒤 확대 — 부드럽고 빠르다."""
    small = Image.new("RGB", (2, len(STOPS)))
    p = small.load()
    for i, (_, l, r) in enumerate(STOPS):
        p[0, i], p[1, i] = l, r
    return small.resize((W, H), Image.BICUBIC)


def nebula(img):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    blobs = [
        (120, 700, 620, (150, 60, 220, 70)),
        (980, 1900, 560, (70, 60, 200, 60)),
        (300, 1500, 480, (120, 50, 200, 45)),
        (820, 380, 420, (110, 70, 210, 50)),
    ]
    for cx, cy, r, col in blobs:
        d.ellipse((cx - r, cy - r * 0.7, cx + r, cy + r * 0.7), fill=col)
    lay = lay.filter(ImageFilter.GaussianBlur(190))
    return Image.alpha_composite(img, lay)


def planet(img, cx, cy, r, tint, ring=True, ring_tilt=0.30):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    if ring:                       # 뒤쪽 고리
        d.ellipse((cx - r * 2.0, cy - r * ring_tilt, cx + r * 2.0, cy + r * ring_tilt),
                  outline=tint + (150,), width=max(3, r // 9))
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=tint + (255,))
    # 구체 음영: 밝은 쪽 + 어두운 쪽
    d.ellipse((cx - r * .85, cy - r * .9, cx + r * .25, cy + r * .1),
              fill=tuple(min(255, c + 45) for c in tint) + (170,))
    d.ellipse((cx - r * .1, cy - r * .1, cx + r * .95, cy + r * .95),
              fill=tuple(max(0, c - 35) for c in tint) + (120,))
    lay = lay.filter(ImageFilter.GaussianBlur(2))
    if ring:                       # 앞쪽 고리 절반
        d2 = ImageDraw.Draw(lay)
        d2.arc((cx - r * 2.0, cy - r * ring_tilt, cx + r * 2.0, cy + r * ring_tilt),
               0, 180, fill=tuple(min(255, c + 30) for c in tint) + (210,),
               width=max(3, r // 9))
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(glow).ellipse((cx - r * 1.5, cy - r * 1.5, cx + r * 1.5, cy + r * 1.5),
                                 fill=tint + (60,))
    glow = glow.filter(ImageFilter.GaussianBlur(60))
    return Image.alpha_composite(Image.alpha_composite(img, glow), lay)


def city(img):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    ground = 2340
    x = -40
    while x < W + 40:
        w = random.randint(55, 130)
        h = random.randint(80, 330)
        top = ground - h
        d.rectangle((x, top, x + w, ground), fill=(96, 82, 210, 52))
        for wy in range(top + 22, ground - 20, 46):      # 창문
            for wx in range(x + 16, x + w - 16, 34):
                if random.random() < 0.45:
                    d.rectangle((wx, wy, wx + 12, wy + 18), fill=(170, 160, 255, 40))
        x += w + random.randint(4, 26)
    lay = lay.filter(ImageFilter.GaussianBlur(1.2))
    return Image.alpha_composite(img, lay)


def stars(img):
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    palette = [(255, 255, 255), (190, 225, 255), (255, 200, 245), (200, 190, 255)]
    for _ in range(520):
        x, y = random.randrange(W), random.randrange(H)
        r = random.choice([1, 1, 1, 1.5, 2, 2, 2.5, 3])
        a = random.randint(70, 235)
        c = random.choice(palette)
        d.ellipse((x - r, y - r, x + r, y + r), fill=c + (a,))
    lay = lay.filter(ImageFilter.GaussianBlur(0.6))

    # 4방향 반짝이
    spark = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(spark)
    for _ in range(26):
        x, y = random.randrange(W), random.randrange(H)
        L = random.randint(16, 46)
        t = max(1, L // 14)
        c = random.choice(palette) + (random.randint(160, 255),)
        ds.polygon([(x, y - L), (x + t, y), (x, y + L), (x - t, y)], fill=c)
        ds.polygon([(x - L, y), (x, y + t), (x + L, y), (x, y - t)], fill=c)
        ds.ellipse((x - t * 2, y - t * 2, x + t * 2, y + t * 2), fill=c)
    glow = spark.filter(ImageFilter.GaussianBlur(9))
    img = Image.alpha_composite(img, lay)
    img = Image.alpha_composite(img, glow)
    return Image.alpha_composite(img, spark)


img = base_gradient().convert("RGBA")
img = nebula(img)
img = city(img)
img = planet(img, 95,  330,  76, (156, 150, 205))
img = planet(img, 985, 1955, 100, (168, 158, 212))
img = planet(img, 150, 2140, 66, (150, 142, 202))
img = planet(img, 1010, 470, 40, (132, 126, 190), ring=False)
img = planet(img, 70,  1180, 30, (140, 130, 198), ring=False)
img = stars(img)
img.convert("RGB").save(OUT)
print("saved", OUT, img.size)
