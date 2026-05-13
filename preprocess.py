import noisereduce as nr
import soundfile as sf
import numpy as np

# Load
data, rate = sf.read("input/her_voice.ogg")

# Reduce noise
reduced = nr.reduce_noise(y=data, sr=rate, prop_decrease=0.8)

# Normalize
normalized = reduced / np.max(np.abs(reduced))

# Save cleaned version
sf.write("input/cleaned.wav", normalized, rate)
print("Done — use input/cleaned.wav as your input now")