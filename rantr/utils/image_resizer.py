from django.core.exceptions import ValidationError
from PIL import Image

def validate_rectangular_image(image):
    image = Image.open(image)
    width, height = image.size
    if width == height:
        raise ValidationError("Uploaded image must be rectangular (not square).")
    return image