import wave
import struct

def compress_wav(input_file, output_file, target_rate=22050):
    """Downsample WAV file to reduce size while maintaining quality"""
    with wave.open(input_file, 'rb') as wav_in:
        params = wav_in.getparams()
        frames = wav_in.readframes(params.nframes)
        
        # Convert to samples
        if params.sampwidth == 2:  # 16-bit
            samples = struct.unpack(f'{params.nframes * params.nchannels}h', frames)
        else:
            print(f"Unsupported sample width: {params.sampwidth}")
            return
        
        # Downsample by taking every nth sample
        original_rate = params.framerate
        downsample_factor = original_rate // target_rate
        
        downsampled = samples[::downsample_factor]
        
        # Write output
        with wave.open(output_file, 'wb') as wav_out:
            wav_out.setnchannels(params.nchannels)
            wav_out.setsampwidth(params.sampwidth)
            wav_out.setframerate(target_rate)
            wav_out.writeframes(struct.pack(f'{len(downsampled)}h', *downsampled))
    
    print(f"Compressed {input_file} -> {output_file}")

# Compress both files
compress_wav('sounds/fanfare.wav', 'sounds/fanfare_compressed.wav')
compress_wav('sounds/faceoff.wav', 'sounds/faceoff_compressed.wav')

print("\nDone! Compressed WAVs created.")
