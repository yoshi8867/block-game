"""hgame/audio 의 원본 wav 를 게임이 쓰는 mp3 로 만든다.

원본 wav 는 플레이 영상 사운드에서 손으로 잘라낸 것이라 구간이 서로 겹친다.
상호상관으로 되짚은 원본 트랙 위치:

    intro                0.500 ~  3.350
    sfx_nice             8.749 ~ 10.169
    sfx_lineclear_9.31   9.250 ~ 10.100   ← nice 안에 통째로 들어 있다 (미사용)
    sfx_perfect         13.966 ~ 14.781
    sfx_timebonus       26.358 ~ 28.091   ← 뒤에 PERFECT 소리가 딸려 왔다
    sfx_gameover        77.898 ~ 80.648

so 잘라낼 구간을 TRIM 에 적어 둔다. 0.40~0.58초가 완전한 무음이라 거기서 끊는다.
"""
import subprocess, os

SRC = r"C:\Users\nutel\OneDrive\Desktop\dev\hgame\audio"
OUT = r"C:\Users\nutel\OneDrive\Desktop\dev\block-game\audio"

# 출력이름: (원본파일, 시작초, 길이초 또는 None=끝까지)
JOBS = {
    "intro":         ("intro.wav", 0, None),
    "bgm_loop":      ("bgm_loop.wav", 0, None),
    "sfx_nice":      ("sfx_nice.wav", 0, None),
    "sfx_perfect":   ("sfx_perfect.wav", 0, None),
    "sfx_gameover":  ("sfx_gameover.wav", 0, None),
    # 0.60초부터 PERFECT 소리가 붙어 있다. 무음 구간에서 자르고 짧게 페이드아웃.
    "sfx_timebonus": ("sfx_timebonus.wav", 0, 0.48),
}

for name, (src, start, dur) in JOBS.items():
    cmd = ["ffmpeg", "-loglevel", "error", "-y"]
    if start:
        cmd += ["-ss", str(start)]
    cmd += ["-i", os.path.join(SRC, src)]
    if dur:
        cmd += ["-t", str(dur), "-af", "afade=t=out:st=%.3f:d=0.04" % (dur - 0.04)]
    cmd += ["-codec:a", "libmp3lame", "-q:a", "5", os.path.join(OUT, name + ".mp3")]
    subprocess.run(cmd, check=True)
    print("%-16s <- %s" % (name + ".mp3", src) + ("  [0~%.2fs 만]" % dur if dur else ""))
