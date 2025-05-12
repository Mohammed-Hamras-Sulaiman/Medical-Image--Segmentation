from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.core.files.storage import default_storage
from .models import MedicalImage, LungSegmentationModel
from .forms import UploadImageForm
from .segmentation import predict_image
from django.conf import settings
import numpy as np
import cv2
import os
import logging
from django.http import HttpResponse
from django.contrib.auth import get_user_model

logger = logging.getLogger(__name__)

@login_required
def upload_image(request):
    """Handles the uploading of images."""
    if request.method == 'POST':
        form = UploadImageForm(request.POST, request.FILES)
        if form.is_valid():
            uploaded_image = form.save(commit=False)
            
            # Assign the logged-in user
            if request.user.is_authenticated:
                uploaded_image.user = request.user
            else:
                # In case of no authenticated user, assign a default user
                default_user = get_user_model().objects.filter(username='default_user').first()
                if default_user:
                    uploaded_image.user = default_user
                else:
                    # Raise an error if default user is not found
                    return HttpResponse("Default user does not exist. Please create a 'default_user'.", status=400)
            
            # Save the image and make sure the id is assigned
            uploaded_image.save()

            # Redirect to the results page with the image id
            return redirect('segmentation:results', image_id=uploaded_image.id)
        else:
            return HttpResponse("Form is not valid. Please check the uploaded file.", status=400)
    else:
        form = UploadImageForm()
    
    return render(request, 'segmentation/upload.html', {'form': form})


def success(request):
    """Renders the success page after an image upload."""
    return render(request, 'segmentation/success.html')


def gallery(request):
    """Displays all uploaded images in the gallery."""
    images = MedicalImage.objects.all()
    return render(request, 'segmentation/gallery.html', {'images': images})


def preprocess_image(image_path):
    """Preprocess the image for the segmentation model."""
    img = cv2.imread(image_path, 0)  # Load image in grayscale
    img_resized = cv2.resize(img, (512, 512))  # Resize to (512, 512)
    img_normalized = img_resized / 255.0  # Normalize to [0, 1]
    img_input = np.expand_dims(img_normalized, axis=-1)  # Add channel dimension
    img_input = np.expand_dims(img_input, axis=0)  # Add batch dimension
    return np.expand_dims(img_input, axis=0)


#def run_segmentation(model, image_path):
    
    """Runs segmentation on an image and saves the resulting mask."""
    try:
        # Load and preprocess the input image
        image = cv2.imread(image_path)
        input_array = preprocess_image(image_path)

        # Perform segmentation prediction
        prediction = model.predict(input_array)[0]
        mask = (prediction > 0.5).astype(np.uint8)

        # Resize mask to match original image size
        mask_resized = cv2.resize(mask, (image.shape[1], image.shape[0]))

        # Define the results directory and result file path
        results_dir = os.path.join('results', 'medical_segmentation')
        os.makedirs(results_dir, exist_ok=True)  # Create results directory if it doesn't exist
        result_filename = f'result_{os.path.basename(image_path)}'
        result_path = os.path.join(results_dir, result_filename)

        # Save the result as an image
        cv2.imwrite(result_path, mask_resized * 255)

        # Return the relative path for rendering in the template
        return result_path
    except Exception as e:
        logger.error(f"Error during segmentation: {str(e)}")
        raise RuntimeError(f"Error during segmentation: {str(e)}")


def view_results(request, image_id):
    image = get_object_or_404(MedicalImage, id=image_id)
    try:
        model = LungSegmentationModel()

        # Log the original image path
        print(f"Original Image Path: {image.image.path}")

        # Load the original image using OpenCV
        original_image = cv2.imread(image.image.path)

        # Predict the segmentation mask
        predicted_mask = model.predict(image.image.path)
        print(f"Predicted Mask: {predicted_mask}")  # Debugging the prediction output
        
        predicted_mask = (predicted_mask > 0.5).astype(np.uint8)

        # Resize the predicted mask to match the original image dimensions
        predicted_mask_resized = cv2.resize(predicted_mask, (original_image.shape[1], original_image.shape[0]))
        print(f"Original Image Shape: {original_image.shape}")
        print(f"Resized Mask Shape: {predicted_mask_resized.shape}")  # Debugging resized mask
        
        # Convert the resized segmentation mask to BGR for overlay
        predicted_mask_bgr = cv2.cvtColor(predicted_mask_resized, cv2.COLOR_GRAY2BGR)

        # Overlay the original image with the resized predicted segmentation mask
        overlaid_image = cv2.addWeighted(original_image, 0.5, predicted_mask_bgr, 0.5, 0)
        print(f"Overlay Image Shape: {overlaid_image.shape}")  # Debugging the overlay

        # Save the overlaid image as a result
        results_dir = os.path.join(settings.MEDIA_ROOT, 'results')
        os.makedirs(results_dir, exist_ok=True)
        print(f"Results Directory: {results_dir}")  # Verify the directory

        result_filename = f'overlay_result_{os.path.basename(image.image.path)}'
        result_path = os.path.join(results_dir, result_filename)
        result_url = f'{settings.MEDIA_URL}results/{result_filename}'
        print(f"Result Path: {result_path}")  # Debugging to ensure correct file saving

        cv2.imwrite(result_path, overlaid_image)

        # Update the database record
        image.segmented_image = f"results/{result_filename}"
        image.save()
        print(f"Database Segmented Image Path: {image.segmented_image}")  # Debugging database update

        result_url = f'{settings.MEDIA_URL}results/{result_filename}'
        print(f"Segmentation Result URL: {image.segmented_image}")
        print(f"Rendered Result URL: {result_url}")

        return render(request, 'segmentation/result.html', {
            'image': image,
            'result_url': result_url,
        })

    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return HttpResponse(f"An error occurred: {str(e)}", status=500)



def segment_lung_view(request):
    """API endpoint for lung segmentation."""
    if request.method == 'POST' and request.FILES.get('image'):
        uploaded_file = request.FILES['image']
        file_path = default_storage.save(uploaded_file.name, uploaded_file)

        try:
            predicted_mask = predict_image(file_path)
            return JsonResponse({'message': 'Segmentation completed successfully!'})
        except Exception as e:
            logger.error(f"Segmentation error: {str(e)}")
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request'}, status=400)


from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import MedicalImage
from django.core.paginator import Paginator
from django.conf import settings
@login_required
def dashboard(request):
    """Displays the user's uploaded images and segmentation results."""
    user_images = MedicalImage.objects.filter(user=request.user)
    for image in user_images:
        print(f"Image ID: {image.id}, Path: {image.image}")
    paginator = Paginator(user_images, 10)  # Show 10 images per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'segmentation/dashboard.html', {
        'page_obj': page_obj,
        'MEDIA_URL': settings.MEDIA_URL,
    })

from django.shortcuts import get_object_or_404, redirect

@login_required
def delete_image(request, image_id):
    """Allows users to delete their uploaded images."""
    image = get_object_or_404(MedicalImage, id=image_id, user=request.user)
    image.delete()
    return redirect('segmentation:dashboard')


