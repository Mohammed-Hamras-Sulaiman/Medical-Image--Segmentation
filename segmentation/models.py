from keras.models import load_model
from .metrics import dice_coefficient, jaccard_index
from django.db import models
import keras 
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
import os
import cv2
import numpy as np

class MedicalImage(models.Model):                                               #image upload by user 
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.SET_NULL,  # Set to NULL if the user is deleted
        null=True,
        blank=True,
        default=None,
    )
    image = models.ImageField(upload_to='uploads/')
    segmented_image = models.ImageField(upload_to='results/', null=True, blank=True)  # Add this field
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):                                                  # image is assaigned to default user if no user found
        if not self.user:
            self.user =  get_user_model().objects.filter(username__in='default_user').first()
        if not self.user:
                raise ValueError("Default user does not exist. Please create a 'default_user'.")

        super().save(*args, **kwargs)
    
    
    
    def __str__(self):
        return self.image.name
    
class LungSegmentationModel(models.Model):
    model_path = os.path.join(settings.BASE_DIR, 'segmentation', 'models', 'unet_mri_xray_trained_model.h5.keras')
    model = load_model(model_path, custom_objects={'dice_coefficient': dice_coefficient, 'jaccard_index': jaccard_index})

    def predict(self, image_path):
        # Preprocess the image
        img = cv2.imread(image_path, 0)  # Load image as grayscale
        img_resized = cv2.resize(img, (512, 512))  # Resize to (512, 512)
        img_normalized = img_resized / 255.0  # Normalize to [0, 1]
        img_input = np.expand_dims(img_normalized, axis=-1)  # Add channel dimension
        img_input = np.expand_dims(img_input, axis=0)  # Add batch dimension

        # Predict the segmentation mask
        pred_mask = self.model.predict(img_input)

        # Postprocess the mask
        pred_mask = np.squeeze(pred_mask)  # Remove batch dimension
        pred_mask = (pred_mask > 0.5).astype(np.uint8)  # Binarize the mask

        return pred_mask
        


#CUSTOMUSER MODEl

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_groups',  # Custom related name
        blank=True
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions',  # Custom related name
        blank=True
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.username
