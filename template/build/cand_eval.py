"""Score candidate voices: Khmer Whisper ASR similarity, median f0, duration, loudness."""
import json, sys, os, subprocess
sys.path.insert(0, 'engine'); sys.path.insert(0, '.')
from khnum import speak
from narrate import vox_python, CAND_SEEDS
from narration import VOICES
import numpy as np, soundfile as sf
jobs = []
for who in sys.argv[1:]:
    for sd in CAND_SEEDS:
        p = os.path.abspath("audio/voices/cand_%s_%d.wav" % (who, sd))
        if os.path.exists(p):
            jobs.append({"id": "%s_%d" % (who, sd), "wav": p, "text": speak(VOICES[who]["sample"])})
json.dump(jobs, open('build/cand_jobs.json', 'w'), ensure_ascii=False)
subprocess.run([vox_python(), 'engine/asr_check.py', 'build/cand_jobs.json', 'build/cand_out.json'], check=True,
               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
for r in json.load(open('build/cand_out.json')):
    y, sr = sf.read('audio/voices/cand_%s.wav' % r['id']); y = y if y.ndim == 1 else y.mean(1)
    f0s = []
    for i in range(0, len(y) - 2048, 1024):
        fr = y[i:i + 2048] * np.hanning(2048)
        if np.sqrt(np.mean(fr ** 2)) < 0.02: continue
        ac = np.correlate(fr, fr, 'full')[2047:]
        lo, hi = int(sr / 450), int(sr / 80); k = lo + np.argmax(ac[lo:hi])
        if ac[k] > 0.3 * ac[0]: f0s.append(sr / k)
    f0 = np.array(f0s)
    print(r['id'], 'asr %.3f' % r['score'], 'f0 med %.0f iqr %.0f' % (np.median(f0), np.percentile(f0, 75) - np.percentile(f0, 25)),
          'dur %.1f' % (len(y) / sr), 'rms %.3f' % np.sqrt(np.mean(y ** 2)), '|', r['hyp'][:60])
