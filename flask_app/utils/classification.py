import torch
import timm
from torchvision import transforms

def initialize_vit_model(model_name='vit_base_patch16_224', num_classes=3, pretrained=False, device=None):
    model = timm.create_model(model_name, pretrained=pretrained, num_classes=num_classes)
    model.to(device)
    model.eval()
    return model

def classify_image(image, model, device, input_size=224):
    transform = transforms.Compose([
        transforms.Resize((input_size, input_size)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])
    image_tensor = transform(image).unsqueeze(0).to(device)
    with torch.no_grad():
        output = model(image_tensor)
    return output
