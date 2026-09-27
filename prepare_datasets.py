from datasets import load_dataset
import os

ds = load_dataset("vankey/RealText-V1")

train_images = ds["train"]

os.makedirs("dataset_images/train/forged", exist_ok=True)
os.makedirs("dataset_images/train/authentic", exist_ok=True)

# Save the first 1000 images for now
for i in range(1000):

    image = train_images[i]["image"]

    if i < 800:
        folder = "dataset_images/train/forged"
    else:
        folder = "dataset_images/train/authentic"

    image.save(os.path.join(folder, f"image_{i}.png"))

print("Images saved successfully!")