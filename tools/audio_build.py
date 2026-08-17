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

intro 만은 손으로 자른 wav 를 쓰지 않고 **두 번째 영상에서 직접 잘라낸다.**
첫 영상의 wav 에는 '띠' 가 세 번밖에 없어서(첫 비프가 잘려 나갔다) 카운트다운이
한 칸씩 밀렸다. 두 번째 영상의 앞 6초에는 네 번이 온전히 들어 있다 —
2.317 / 3.333 / 4.308 / 5.317(0.63초 긴소리). 1% 문턱에서도 같은 값이다.
그래서 첫 '띠' 17ms 앞에서 잘라 4.0초(=카운트다운 전체)를 뜬다.
그러면 긴 '띠—' 가 3.000초 지점, 즉 GO! 가 뜨는 순간에 온다.
(영상의 텍스트는 2.15/3.15/4.15/5.15 에 바뀐다. 소리가 0.17초 늦는데
 이는 화면녹화의 A/V 지연이므로 소리 쪽을 기준으로 삼는다.)
"""
import subprocess, os

SRC = r"C:\Users\nutel\OneDrive\Desktop\dev\hgame\audio"
OUT = r"C:\Users\nutel\OneDrive\Desktop\dev\block-game\audio"
VIDEO2 = r"C:\Users\nutel\OneDrive\Desktop\dev\hgame\KakaoTalk_20260817_032722265.mp4"

# 출력이름: (원본파일, 시작초, 길이초 또는 None=끝까지)
JOBS = {
    "intro":         (VIDEO2, 2.300, 4.0),
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
    cmd += ["-i", src if os.path.isabs(src) else os.path.join(SRC, src)]
    if dur:
        cmd += ["-t", str(dur), "-af", "afade=t=out:st=%.3f:d=0.04" % (dur - 0.04)]
    cmd += ["-vn", "-codec:a", "libmp3lame", "-q:a", "5",
            os.path.join(OUT, name + ".mp3")]
    subprocess.run(cmd, check=True)
    print("%-16s <- %s" % (name + ".mp3", os.path.basename(src))
          + ("  [%.3f~%.3fs]" % (start, start + dur) if dur else ""))
