Design the AI Engine.

Support Plugin Architecture.

Plugins include

Segmentation

Registration

Classification

Detection

Reconstruction

Implant Generation

Every plugin should implement

initialize()

load_model()

predict()

postprocess()

metadata()

cleanup()

Design interfaces only.

No implementation.
