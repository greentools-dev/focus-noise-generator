# GreenTools Focus Audio Engine // Soundscapes & Lo-Fi Stems

This directory contains the manifest and specifications for the royalty-free CC0 ambient soundscape loops used by `focus-noise-generator`.

### Channel 1: Multi-Track Acoustic Soundscapes
1. **`lo-fi-study.wav`**: Warm analog electric piano (Rhodes-style) chord progression with gentle sidechain compression and tape warmth.
2. **`deep-rain.wav`**: High-fidelity field recording of rain against glass with low-frequency rolling thunder.
3. **`vinyl-tape.wav`**: 33⅓ RPM turntable groove noise, authentic micro-dust crackle, and subtle tape wow & flutter.
4. **`cosmic-drone.wav`**: 432 Hz Pythagorean tuning resonant ambient pad with detuned supersaw voices and slow low-pass breathing sweeps.

### Channel 2: Neural Modulation Engine (Brain.fm-Style Binaural DSP)
Synthesized in real-time via Web Audio API `ChannelMergerNode(2)` delivering precise stereo phase beat frequencies:
- **Alpha Flow**: 210 Hz (L) / 220 Hz (R) -> 10.0 Hz Binaural Beat (Deep work, coding sprints, reading flow)
- **Beta Focus**: 240 Hz (L) / 258 Hz (R) -> 18.0 Hz Binaural Beat (High-alert analytical tasks, debugging, complex logic)
- **Theta Reset**: 180 Hz (L) / 186 Hz (R) -> 6.0 Hz Binaural Beat (Creative brainstorming, ideation, calm recovery)

All procedural audio buffers are synthesized dynamically in browser memory at 48kHz 32-bit floating point, providing 100% offline, zero-latency execution with zero telemetry.
