# GreenTools Focus Audio Engine // Soundscapes & Lo-Fi Stems

This directory contains the production royalty-free CC0 / Public Domain loop assets used by `focus-noise-generator`.

### Channel 1: Multi-Track Acoustic Soundscapes
1. **`lofi-study.mp3`** (CC0 / Public Domain)
   - **Type**: Analog electric Rhodes piano chord progression loop with smooth room decay.
   - **Musical Structure**: Dm9 → G13 → Cmaj9 → Am9 with lush harmonic tines, hammer clink transient modeling, and lo-fi sidechain breathing.
   - **Format**: 44.1 kHz, 192 kbps Stereo MP3, seamless equal-power wrap-around crossfade loop.

2. **`deep-rain.mp3`** (CC0 / Public Domain)
   - **Type**: Field-recorded binaural rain with rolling sub-bass thunder.
   - **Acoustic Characteristics**: High-fidelity rain droplets on glass combined with 35–85 Hz sub-bass rolling thunder swells.
   - **Format**: 44.1 kHz, 192 kbps Stereo MP3, seamless equal-power crossfade loop.

3. **`vinyl-tape.mp3`** (CC0 / Public Domain)
   - **Type**: Authentic 33⅓ RPM vinyl surface warmth and micro-dust crackle.
   - **Acoustic Characteristics**: Real turntable groove friction noise, micro-dust crackle, 50 Hz motor hum harmonics, and subtle analog tape flutter.
   - **Format**: 44.1 kHz, 192 kbps Stereo MP3, seamless equal-power crossfade loop.

4. **`cosmic-drone.mp3`** (CC0 / Public Domain)
   - **Type**: Resonant 432 Hz Pythagorean ambient soundscape.
   - **Acoustic Characteristics**: Sacred 432 Hz master carrier with sub-octave drone (108 Hz, 216 Hz), 5-voice detuned celestial choir, 648 Hz fifth harmonic, and slow-breathing resonant lowpass filter sweeps.
   - **Format**: 44.1 kHz, 192 kbps Stereo MP3, seamless zero-crossing phase-aligned loop.

### Channel 2: Neural Modulation Engine (Brain.fm-Style Binaural DSP)
Synthesized in real-time via Web Audio API `ChannelMergerNode(2)` delivering precise stereo phase beat frequencies:
- **Alpha Flow**: 210 Hz (L) / 220 Hz (R) -> 10.0 Hz Binaural Beat (Deep work, coding sprints, reading flow)
- **Beta Focus**: 240 Hz (L) / 258 Hz (R) -> 18.0 Hz Binaural Beat (High-alert analytical tasks, debugging, complex logic)
- **Theta Reset**: 180 Hz (L) / 186 Hz (R) -> 6.0 Hz Binaural Beat (Creative brainstorming, ideation, calm recovery)

### Architecture & Zero-Click Looping Guarantee
- Stems are fetched as binary buffers and decoded natively via `AudioContext.decodeAudioData()`.
- Continuous loops run in browser hardware via Web Audio `AudioBufferSourceNode` (`loop = true`).
- Audio buffers undergo automated border-conditioning in memory to eliminate encoder silence padding and ensure zero click/pop gaps.
- 100% private, client-side, zero telemetry.
