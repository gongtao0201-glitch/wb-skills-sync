# 逐幕 TTS 配音 → 用配音时长反推每幕 dur → 输出对齐后的 scenes.json 与整轨语音
# 用法: python tts_scenes.py <script.json> <scenes.json> <outdir> [--voice=zh-CN-YunyangNeural] [--rate=+0%] [--pad=0.7]
import asyncio, json, os, re, subprocess, sys, shutil

def arg(name, default):
    for a in sys.argv[1:]:
        if a.startswith(f"--{name}="):
            return a.split("=", 1)[1]
    return default

FFMPEG = arg("ffmpeg", r"D:/obsidian 笔记(五鼎源)/09-0全域创业素材/Tools/ffmpeg/ffmpeg.exe")
VOICE  = arg("voice", "zh-CN-YunyangNeural")
RATE   = arg("rate", "+0%")
PAD    = float(arg("pad", "0.7"))

DESENIOR = [
    (r"中老年人?", "爱折腾的哥哥姐姐"),
    (r"银发(人群|族)?", "爱折腾的"),
    (r"老年人", "哥哥姐姐"),
    (r"老人家", "哥哥姐姐"),
]

def desenior(t: str) -> str:
    for pat, rep in DESENIOR:
        t = re.sub(pat, rep, t)
    return t

def duration(path):
    out = subprocess.run([FFMPEG, "-hide_banner", "-i", path],
                         capture_output=True, text=True, encoding="utf-8", errors="ignore").stderr
    m = re.search(r"Duration:\s*(\d+):(\d+):([\d.]+)", out)
    if not m:
        raise RuntimeError(f"测不到时长: {path}")
    return int(m[1]) * 3600 + int(m[2]) * 60 + float(m[3])

async def tts(text, path):
    import edge_tts
    c = edge_tts.Communicate(text, VOICE, rate=RATE)
    await c.save(path)

def main():
    script_p, scenes_p, outdir = sys.argv[1], sys.argv[2], sys.argv[3]
    script = json.load(open(script_p, encoding="utf-8"))
    scenes_data = json.load(open(scenes_p, encoding="utf-8"))
    scenes = scenes_data["scenes"]
    os.makedirs(outdir, exist_ok=True)
    seg_dir = os.path.join(outdir, "_seg")
    os.makedirs(seg_dir, exist_ok=True)

    lines = script if isinstance(script, list) else script["lines"]
    if len(lines) != len(scenes):
        print(f"[tts] ⚠️ 台词 {len(lines)} 条 vs 幕 {len(scenes)} 幕，数量不一致，按较小值对齐")
    n = min(len(lines), len(scenes))

    # 1) 逐段合成
    for i in range(n):
        text = desenior(lines[i]["text"] if isinstance(lines[i], dict) else lines[i])
        p = os.path.join(seg_dir, f"seg{i:02d}.mp3")
        if not os.path.exists(p):
            asyncio.run(tts(text, p))
        print(f"[tts] {i+1}/{n} {duration(p):.2f}s  {text[:24]}…")

    # 2) 逐段补尾部静音，使该段音频时长 = 该幕 dur
    padded, timing, t_cursor = [], [], 0.0
    for i in range(n):
        raw = duration(os.path.join(seg_dir, f"seg{i:02d}.mp3"))
        pad = PAD + (0.3 if i == 0 else 0) + (0.8 if i == n - 1 else 0)
        dur = max(2.6, raw + pad)
        out = os.path.join(seg_dir, f"pad{i:02d}.mp3")
        # 注：本机 ffmpeg(N-92722) 不支持 apad=pad_dur=，用 apad + -t 截取到目标时长
        subprocess.run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
                        "-i", os.path.join(seg_dir, f"seg{i:02d}.mp3"),
                        "-af", "apad", "-t", f"{dur:.3f}", "-c:a", "libmp3lame", "-b:a", "192k", out],
                       check=True)
        padded.append(out)
        timing.append({"i": i, "type": scenes[i].get("type"), "audio": round(raw, 2),
                       "dur": round(dur, 2), "start": round(t_cursor, 2)})
        scenes[i]["dur"] = round(dur, 2)
        t_cursor += dur

    # 3) 拼接整轨
    listfile = os.path.join(seg_dir, "concat.txt")
    with open(listfile, "w", encoding="utf-8") as f:
        for p in padded:
            f.write("file '" + os.path.abspath(p).replace("\\", "/") + "'\n")
    voice = os.path.join(outdir, "voice.mp3")
    subprocess.run([FFMPEG, "-y", "-hide_banner", "-loglevel", "error",
                    "-f", "concat", "-safe", "0", "-i", listfile,
                    "-c:a", "libmp3lame", "-b:a", "192k", voice], check=True)

    total = sum(s["dur"] for s in scenes)
    json.dump(scenes_data, open(os.path.join(outdir, "scenes_vo.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)
    json.dump({"voice": VOICE, "rate": RATE, "total": round(total, 2), "timing": timing},
              open(os.path.join(outdir, "timing.json"), "w", encoding="utf-8"),
              ensure_ascii=False, indent=2)

    print(f"\n[tts] 整轨 {voice}  {duration(voice):.2f}s")
    print(f"[tts] 分幕时长 {' + '.join(str(s['dur']) for s in scenes)} = {total:.2f}s")
    print(f"[tts] → scenes_vo.json / timing.json")

if __name__ == "__main__":
    main()
