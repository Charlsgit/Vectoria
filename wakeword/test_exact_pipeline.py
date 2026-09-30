import numpy as np
import onnxruntime as ort
from openwakeword.data import augment_clips
from openwakeword.utils import AudioFeatures

AUDIO = "wakeword/training/output/oww_training/hey_vectoria/positive_test/0.wav"
MODEL = "wakeword/training/output/oww_training/hey_vectoria.onnx"

# Use the same preprocessing function used during training
generator = augment_clips(
    [AUDIO],
    total_length=32000,
    batch_size=1,
    background_clip_paths=[],
    RIR_paths=[]
)

audio_batch = next(generator)

print("Augmented audio shape:", audio_batch.shape)
print("Audio dtype:", audio_batch.dtype)

# Convert the augmented audio into the same OpenWakeWord embeddings
features = AudioFeatures()
embeddings = features.embed_clips(audio_batch)

print("Embedding shape:", embeddings.shape)

# Model expects [1, 16, 96]
input_features = embeddings[:, -16:, :].astype(np.float32)

session = ort.InferenceSession(MODEL)
input_name = session.get_inputs()[0].name

score = session.run(None, {input_name: input_features})[0][0][0]

print("ONNX score:", float(score))
