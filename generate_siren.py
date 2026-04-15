import wave
import struct
import math

sample_rate = 44100
duration = 2.0
max_amp = 32767
freq_start = 440.0
freq_end = 880.0
n_samples = int(sample_rate * duration)

with wave.open('siren.wav', 'w') as wav:
    wav.setnchannels(1)
    wav.setsampwidth(2)
    wav.setframerate(sample_rate)
    for i in range(n_samples):
        t = i / sample_rate
        freq = freq_start + (freq_end - freq_start) * (0.5 - 0.5 * math.cos(math.pi * t / duration))
        value = int(max_amp * 0.5 * math.sin(2 * math.pi * freq * t) * (1 - t / duration))
        wav.writeframes(struct.pack('<h', value))

print('siren.wav created')
