from __future__ import print_function, division

import torch
from torchvision import transforms
from PIL import Image
import torchvision.transforms as transforms


# Подача изображения

def predict_parasite(image_path, model, class_names):

    image = Image.open(image_path)

    preprocess = transforms.Compose([
        transforms.RandomResizedCrop(224),
        transforms.RandomHorizontalFlip(),
        transforms.Grayscale(num_output_channels=3),
        transforms.ToTensor(),
        transforms.Normalize([0.485], [0.229])
    ])

    input = preprocess(image).unsqueeze(0)
    was_training = model.training
    model.eval()

    with torch.no_grad():
        outputs = model(input)
        _, preds = torch.max(outputs, 1)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)

        a = class_names
        b = probabilities[0]

        combined = list(zip(a, b))
        sorted_combined = sorted(combined, key=lambda x: x[1], reverse=True)

        sorted_a, sorted_b = zip(*sorted_combined)
        sorted_a = list(sorted_a)
        sorted_b = list(sorted_b)

        return class_names[preds[0]]