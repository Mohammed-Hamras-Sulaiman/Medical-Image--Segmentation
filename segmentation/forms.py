from django.core.validators import FileExtensionValidator
from django import forms
from .models import MedicalImage
import logging

logger = logging.getLogger(__name__)
# Create a form for uploading images
class UploadImageForm(forms.ModelForm):
    class Meta:
        # Specifies the model this form is linked to
        model = MedicalImage
        # Specifies the fields that the form will include
        fields = ['image']
    image = forms.ImageField(
        validators=[
            FileExtensionValidator(['jpg', 'jpeg', 'png'], message="Only jpg, jpeg, and png extensions are allowed.")
        ]
    )
     
    
    def clean_image(self):
        image = self.cleaned_data.get('image')
        logger.debug(f"Validating file: {image.name}")
        if not image:
            raise forms.ValidationError("Please upload an image.")
    
        max_size = 5 * 1024 * 1024
        if image.size > max_size:
            logger.debug("File size exceeds 5MB.")
            raise forms.ValidationError("File size cannot exceed 5MB.")
    
        if not image.name.endswith(('.jpg', '.jpeg', '.png')):
            logger.debug("Invalid file extension.")
            raise forms.ValidationError("Only images with jpg, jpeg, and png extensions are allowed.")
    
        logger.debug("File is valid.")
        return image