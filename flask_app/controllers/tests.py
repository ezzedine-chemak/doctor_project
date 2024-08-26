from flask import Flask, request, render_template, redirect, url_for
from werkzeug.utils import secure_filename
import os
from PIL import Image
import torch
from flask_app.utils.segmentation import preprocess_image, inference, apply_mask, MALUNet
from flask_app.utils.classification import initialize_vit_model, classify_image
import matplotlib.pyplot as plt
import numpy as np
from flask_app import app
#pipenv  install flask torch torchvision timm pillow matplotlib numpy pymysql flask-bcrypt
#   pipenv install "numpy<2"

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
segmentation_model_path = 'flask_app/models/segmentation_model.pth'
classification_model_path = 'flask_app/models/classification_model.pth'

segmentation_model = MALUNet()
segmentation_model.load_state_dict(torch.load(segmentation_model_path, map_location=device), strict=False)
segmentation_model.to(device)
segmentation_model.eval()

classification_model = initialize_vit_model('vit_tiny_patch16_224', num_classes=3, pretrained=False, device=device)
classification_model.load_state_dict(torch.load(classification_model_path, map_location=device))
classification_model.to(device)
classification_model.eval()

class_labels = ['Melanoma', 'Seborrheic Keratosis', 'Nevus']

@app.route('/upload_image', methods=['GET', 'POST'])
def upload_image():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            return redirect(url_for('results', filename=filename))
    return render_template('dashboard.html')

@app.route('/resul', methods=['POST'])
def resul():
    if 'doctor_id' not in session:
        return redirect('/logout')

    return render_template('dashboard.html')


@app.route('/results/<filename>')
def results(filename):
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    original_image = Image.open(image_path).convert('RGB')

    desired_size = (256, 256)
    original_image = original_image.resize(desired_size)
    
    segmentation_tensor = preprocess_image(image_path, size=desired_size, normalize=False)
    segmentation_output = inference(segmentation_model, segmentation_tensor, device)
    segmentation_mask = segmentation_output.cpu().squeeze(0).squeeze(0) > 0.5
    segmentation_mask_image = Image.fromarray(np.uint8(segmentation_mask) * 255).resize(desired_size)
    masked_image = apply_mask(original_image, segmentation_mask_image).resize(desired_size)

    classification_output = classify_image(masked_image, classification_model, device)
    predicted_class_idx = torch.argmax(classification_output, dim=1).item()
    predicted_class = class_labels[predicted_class_idx]

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    title_fontsize = 20

    # Ajouter de l'espace au-dessus des images
    fig.subplots_adjust(top=0.85)

    # Appliquer des styles pour rendre le texte plus clair
    axes[0].imshow(original_image)
    axes[0].set_title('Original Image', fontsize=title_fontsize, fontweight='bold')
    axes[0].axis('off')

    axes[1].imshow(segmentation_mask, alpha=0.5, cmap='jet')
    axes[1].set_title('Segmentation Output', fontsize=title_fontsize, fontweight='bold')
    axes[1].axis('off')

    axes[2].imshow(masked_image)
    axes[2].set_title(f'Classification: {predicted_class}', fontsize=title_fontsize, fontweight='bold')
    axes[2].axis('off')

    plt.tight_layout()
    results_image_path = os.path.join(app.config['UPLOAD_FOLDER'], f'results_{filename}')
    plt.savefig(results_image_path)
    plt.close()

    return render_template('results.html', original_image=url_for('static', filename=f'uploads/{filename}'),
                           results_image=url_for('static', filename=f'uploads/results_{filename}'),
                           predicted_class=predicted_class)


if __name__ == '__main__':
    app.run(debug=True)

