import numpy as np
import wave
import subprocess
import os

AUDIO_DIR = os.path.dirname(os.path.abspath(__file__))
SR = 44100

def save_wav(filename, data_l, data_r, sr=SR):
    # Ensure float in range [-1.0, 1.0]
    peak = max(np.max(np.abs(data_l)), np.max(np.abs(data_r)))
    if peak > 0.98:
        scale = 0.98 / peak
        data_l = data_l * scale
        data_r = data_r * scale

    int_l = (data_l * 32767.0).astype(np.int16)
    int_r = (data_r * 32767.0).astype(np.int16)
    interleaved = np.empty((len(int_l) * 2,), dtype=np.int16)
    interleaved[0::2] = int_l
    interleaved[1::2] = int_r

    wav_path = os.path.join(AUDIO_DIR, filename)
    with wave.open(wav_path, 'wb') as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(interleaved.tobytes())
    return wav_path

def convert_to_mp3(wav_path, mp3_filename, bitrate='192k'):
    mp3_path = os.path.join(AUDIO_DIR, mp3_filename)
    cmd = [
        'ffmpeg', '-y', '-i', wav_path,
        '-codec:a', 'libmp3lame', '-b:a', bitrate,
        '-ar', str(SR),
        mp3_path
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    if os.path.exists(wav_path):
        os.remove(wav_path)
    print(f"Generated {mp3_filename} ({os.path.getsize(mp3_path)} bytes)")
    return mp3_path

def apply_seamless_crossfade(data_l, data_r, crossfade_sec=1.5, sr=SR):
    xfade_samples = int(crossfade_sec * sr)
    total_samples = len(data_l)
    out_len = total_samples - xfade_samples

    # Equal power crossfade curves
    t = np.linspace(0, 1, xfade_samples)
    fade_in = np.sin(0.5 * np.pi * t)
    fade_out = np.cos(0.5 * np.pi * t)

    res_l = np.zeros(out_len, dtype=np.float32)
    res_r = np.zeros(out_len, dtype=np.float32)

    # Core middle
    res_l[:out_len] = data_l[:out_len]
    res_r[:out_len] = data_r[:out_len]

    # Crossfade head and tail
    tail_l = data_l[out_len:total_samples]
    tail_r = data_r[out_len:total_samples]

    res_l[:xfade_samples] = res_l[:xfade_samples] * fade_in + tail_l * fade_out
    res_r[:xfade_samples] = res_r[:xfade_samples] * fade_in + tail_r * fade_out

    return res_l, res_r

# ==========================================
# 1. LO-FI STUDY BEATS (Rhodes Piano Loop)
# ==========================================
def build_lofi_study():
    print("Building lofi-study.mp3...")
    bpm = 70
    beat_sec = 60.0 / bpm
    bar_sec = beat_sec * 4.0
    num_bars = 4
    total_dur = bar_sec * num_bars + 3.0 # Extra 3s for tail crossfade
    total_samples = int(total_dur * SR)

    out_l = np.zeros(total_samples, dtype=np.float32)
    out_r = np.zeros(total_samples, dtype=np.float32)

    # Chords: Dm9, G13, Cmaj9, Am9
    chord_voicings = [
        # Dm9: D3, F3, A3, C4, E4
        [146.83, 174.61, 220.00, 261.63, 329.63],
        # G13: G2, F3, B3, E4, A4
        [98.00, 174.61, 246.94, 329.63, 440.00],
        # Cmaj9: C3, E3, G3, B3, D4
        [130.81, 164.81, 196.00, 246.94, 293.66],
        # Am9: A2, G3, C4, E4, B4
        [110.00, 196.00, 261.63, 329.63, 493.88]
    ]

    for bar_idx, freqs in enumerate(chord_voicings):
        start_t = bar_idx * bar_sec
        start_samp = int(start_t * SR)
        note_dur = bar_sec + 2.5
        note_samples = int(note_dur * SR)

        for f_idx, freq in enumerate(freqs):
            t_note = np.linspace(0, note_dur, note_samples, endpoint=False)
            # Physical tine decay envelope
            tine_decay = np.exp(-t_note / (2.2 + 100.0 / (freq + 40.0)))
            # Attack smooth curve (10ms)
            attack = np.minimum(1.0, t_note * 100.0)
            # Hammer clink transient (high non-harmonic burst)
            hammer = np.sin(2 * np.pi * (freq * 4.12) * t_note) * np.exp(-t_note / 0.02) * 0.25
            # Bell overtone
            bell = np.sin(2 * np.pi * (freq * 2.76) * t_note) * np.exp(-t_note / 0.4) * 0.2

            # Fundamental + 2nd + 3rd harmonics
            tine = (
                np.sin(2 * np.pi * freq * t_note) * 1.0 +
                np.sin(2 * np.pi * freq * 2.001 * t_note) * 0.32 +
                np.sin(2 * np.pi * freq * 3.003 * t_note) * 0.08
            )

            # Tremolo LFO
            tremolo = 1.0 + 0.035 * np.sin(2 * np.pi * 4.2 * t_note)

            wave_sig = (tine * tine_decay + bell + hammer) * attack * tremolo * 0.16

            # Gentle stereo spread across chord voices
            pan = (f_idx / (len(freqs) - 1) - 0.5) * 0.6
            left_gain = 0.5 * (1.0 - pan)
            right_gain = 0.5 * (1.0 + pan)

            end_samp = min(total_samples, start_samp + note_samples)
            actual_len = end_samp - start_samp

            out_l[start_samp:end_samp] += wave_sig[:actual_len] * left_gain
            out_r[start_samp:end_samp] += wave_sig[:actual_len] * right_gain

    # Room decay reverb simulation via multi-tap delays
    t_axis = np.linspace(0, total_dur, total_samples, endpoint=False)
    rev_l = np.zeros_like(out_l)
    rev_r = np.zeros_like(out_r)
    room_delays = [0.031, 0.047, 0.063, 0.089, 0.117, 0.143]
    for idx, d in enumerate(room_delays):
        d_samp = int(d * SR)
        gain = 0.22 * (0.8 ** idx)
        rev_l[d_samp:] += out_r[:-d_samp] * gain
        rev_r[d_samp:] += out_l[:-d_samp] * gain

    out_l = out_l * 0.75 + rev_l * 0.25
    out_r = out_r * 0.75 + rev_r * 0.25

    # Lo-fi sidechain pumping modulation (every beat)
    beat_phase = (t_axis / beat_sec) % 1.0
    sidechain = 0.65 + 0.35 * np.sin(beat_phase * np.pi)
    out_l *= sidechain
    out_r *= sidechain

    # Analog tape saturation
    out_l = np.tanh(out_l * 1.5) * 0.65
    out_r = np.tanh(out_r * 1.5) * 0.65

    # Seamless crossfade
    res_l, res_r = apply_seamless_crossfade(out_l, out_r, crossfade_sec=2.5, sr=SR)
    wav_path = save_wav('lofi-temp.wav', res_l, res_r)
    return convert_to_mp3(wav_path, 'lofi-study.mp3')

# ==========================================
# 2. DEEP RAIN & ROLLING THUNDER
# ==========================================
def build_deep_rain():
    print("Building deep-rain.mp3...")
    # Sourced from David Öhlin's rain & thunder + Wikimedia storm recordings
    # Extract 30 seconds of high fidelity binaural rain and thunder
    src_wav = os.path.join(AUDIO_DIR, 'rain_src.wav')
    cmd = [
        'ffmpeg', '-y', '-i', 'rain_test.ogg',
        '-af', 'highpass=f=20,lowpass=f=12000,volume=1.8',
        src_wav
    ]
    subprocess.run(cmd, check=True, capture_output=True)

    with wave.open(src_wav, 'rb') as w:
        frames = w.readframes(w.getnframes())
        raw = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0

    os.remove(src_wav)

    # Make stereo binaural: left is source, right has 0.4ms interaural time difference + subtle eq
    dur = len(raw) / SR
    t = np.linspace(0, dur, len(raw), endpoint=False)

    rain_l = raw.copy()
    shift = int(0.0004 * SR)
    rain_r = np.roll(raw, shift) * 0.95

    # Enrich with rolling sub-bass thunder swell around 40-70Hz
    thunder_t = t % 12.0
    thunder_env1 = np.exp(-((thunder_t - 3.5) / 1.8) ** 2)
    thunder_env2 = np.exp(-((thunder_t - 9.0) / 2.2) ** 2)
    thunder_sub = (
        np.sin(2 * np.pi * 42.0 * t + np.sin(2 * np.pi * 8.0 * t)) * 0.35 +
        np.sin(2 * np.pi * 58.0 * t) * 0.25
    )
    rain_l += thunder_sub * (thunder_env1 * 0.45 + thunder_env2 * 0.35)
    rain_r += thunder_sub * (thunder_env1 * 0.55 + thunder_env2 * 0.40)

    # Soft limiter / saturation
    rain_l = np.tanh(rain_l * 1.2) * 0.75
    rain_r = np.tanh(rain_r * 1.2) * 0.75

    # Seamless crossfade loop
    res_l, res_r = apply_seamless_crossfade(rain_l, rain_r, crossfade_sec=2.0, sr=SR)
    wav_path = save_wav('rain-temp.wav', res_l, res_r)
    return convert_to_mp3(wav_path, 'deep-rain.mp3')

# ==========================================
# 3. AUTHENTIC VINYL & TAPE WARMTH
# ==========================================
def build_vinyl_tape():
    print("Building vinyl-tape.mp3...")
    # Extract 30 seconds of authentic 33.3 RPM vinyl crackle from vinyl_test.mp3
    src_wav = os.path.join(AUDIO_DIR, 'vinyl_src.wav')
    cmd = [
        'ffmpeg', '-y', '-ss', '00:00:05', '-t', '32',
        '-i', 'vinyl_test.mp3',
        '-af', 'volume=2.2',
        src_wav
    ]
    subprocess.run(cmd, check=True, capture_output=True)

    with wave.open(src_wav, 'rb') as w:
        nch = w.getnchannels()
        frames = w.readframes(w.getnframes())
        raw = np.frombuffer(frames, dtype=np.int16).reshape(-1, nch).astype(np.float32) / 32768.0

    os.remove(src_wav)

    v_l = raw[:, 0]
    v_r = raw[:, 1]
    total_len = len(v_l)
    t = np.linspace(0, total_len / SR, total_len, endpoint=False)

    # Turntable 33⅓ RPM motor groove hum (50Hz ground loop + 100Hz 2nd harmonic)
    groove_hum = (np.sin(2 * np.pi * 50.0 * t) * 0.04 + np.sin(2 * np.pi * 100.0 * t) * 0.02)
    # Subtle tape flutter (0.35 Hz wow)
    flutter = np.sin(2 * np.pi * 0.35 * t) * 0.015

    v_l = v_l + groove_hum + flutter
    v_r = v_r + groove_hum * 0.95 + flutter * 0.9

    # Analog tape saturation
    v_l = np.tanh(v_l * 1.3) * 0.7
    v_r = np.tanh(v_r * 1.3) * 0.7

    res_l, res_r = apply_seamless_crossfade(v_l, v_r, crossfade_sec=2.0, sr=SR)
    wav_path = save_wav('vinyl-temp.wav', res_l, res_r)
    return convert_to_mp3(wav_path, 'vinyl-tape.mp3')

# ==========================================
# 4. COSMIC DRONE (432 Hz Pythagorean Pad)
# ==========================================
def build_cosmic_drone():
    print("Building cosmic-drone.mp3...")
    duration = 24.0 # 24 seconds loop
    total_samples = int(duration * SR)
    t = np.linspace(0, duration, total_samples, endpoint=False)

    # 432 Hz Pythagorean sacred tuning frequencies
    base_f = 432.0
    sub_f = 216.0
    low_f = 108.0
    fifth_f = 648.0 # 3:2 ratio

    # Detuned voices for rich, shimmering supersaw pad
    detune_spread = [-1.4, -0.6, 0.0, 0.7, 1.5]
    pad_l = np.zeros(total_samples, dtype=np.float32)
    pad_r = np.zeros(total_samples, dtype=np.float32)

    for i, d in enumerate(detune_spread):
        f = base_f + d
        pan = (i / (len(detune_spread) - 1) - 0.5) * 0.8
        # Gentle saw with warm roll-off (odd + even harmonics)
        voice = (
            np.sin(2 * np.pi * f * t) * 0.45 +
            np.sin(4 * np.pi * f * t) * 0.18 +
            np.sin(6 * np.pi * f * t) * 0.08
        )
        pad_l += voice * 0.5 * (1.0 - pan)
        pad_r += voice * 0.5 * (1.0 + pan)

    # Sub-bass foundation (108 Hz and 216 Hz)
    sub = (np.sin(2 * np.pi * low_f * t) * 0.4 + np.sin(2 * np.pi * sub_f * t) * 0.35)
    pad_l += sub * 0.5
    pad_r += sub * 0.5

    # Fifth overtone harmonic (648 Hz) with slow celestial breathing
    fifth = np.sin(2 * np.pi * fifth_f * t) * 0.15
    pad_l += fifth * 0.4
    pad_r += fifth * 0.6

    # Slow breathing resonant filter sweep (0.04167 Hz = exactly 1 cycle per 24s)
    # This guarantees exact phase alignment at loop boundary!
    sweep = 0.65 + 0.35 * np.cos(2 * np.pi * (1.0 / duration) * t)
    pad_l *= sweep
    pad_r *= (1.3 - 0.3 * sweep)

    # Analog warmth saturation
    pad_l = np.tanh(pad_l * 1.2) * 0.65
    pad_r = np.tanh(pad_r * 1.2) * 0.65

    # Seamless crossfade (1.5s)
    res_l, res_r = apply_seamless_crossfade(pad_l, pad_r, crossfade_sec=1.5, sr=SR)
    wav_path = save_wav('drone-temp.wav', res_l, res_r)
    return convert_to_mp3(wav_path, 'cosmic-drone.mp3')

if __name__ == '__main__':
    build_lofi_study()
    build_deep_rain()
    build_vinyl_tape()
    build_cosmic_drone()
    print("All stems successfully created!")
