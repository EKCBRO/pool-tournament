"""Generate sound effects for Pool Tournament App"""
import wave
import struct
import math

def generate_tone(frequency, duration, sample_rate=44100, volume=0.3):
    """Generate a sine wave tone"""
    num_samples = int(sample_rate * duration)
    samples = []
    for i in range(num_samples):
        value = volume * math.sin(2 * math.pi * frequency * i / sample_rate)
        samples.append(int(value * 32767))
    return samples

def generate_fanfare():
    """Generate a triumphant fanfare sound"""
    sample_rate = 44100
    samples = []
    
    # Triumphant ascending notes (C-E-G-C major chord)
    notes = [
        (523, 0.15),  # C5
        (659, 0.15),  # E5
        (784, 0.15),  # G5
        (1047, 0.4),  # C6 (held longer)
    ]
    
    for freq, duration in notes:
        samples.extend(generate_tone(freq, duration, sample_rate, 0.6))  # Increased volume
    
    # Write to WAV file
    with wave.open('sounds/fanfare.wav', 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(struct.pack('h' * len(samples), *samples))
    
    print("✓ fanfare.wav created")

def generate_faceoff():
    """Generate dramatic face-off music"""
    sample_rate = 44100
    samples = []
    
    # Dramatic low notes building tension (D-F-A pattern)
    notes = [
        (146.83, 0.3),  # D3
        (174.61, 0.3),  # F3
        (220.00, 0.3),  # A3
        (146.83, 0.15), # D3 quick
        (220.00, 0.4),  # A3 held
    ]
    
    for freq, duration in notes:
        samples.extend(generate_tone(freq, duration, sample_rate, 0.55))  # Increased volume
    
    # Write to WAV file
    with wave.open('sounds/faceoff.wav', 'w') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(struct.pack('h' * len(samples), *samples))
    
    print("✓ faceoff.wav created")

if __name__ == '__main__':
    print("Generating sound effects...")
    generate_fanfare()
    generate_faceoff()
    print("\nSound files created in sounds/ folder!")
