from django.urls import path,include
from . import views # Import your view
from django.contrib.auth import views as auth_views
app_name = 'segmentation'
urlpatterns = [
    path('upload/', views.upload_image, name='upload_image'),
    path('success/', views.success, name='success'),
    path('gallery/', views.gallery, name='gallery'),
    path('results/<int:image_id>/', views.view_results, name='results'),
    path('segment-lung/', views.segment_lung_view, name='segment_lung'),
    #path('segmentation/upload/', views.upload_image, name='upload'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('delete/<int:image_id>/', views.delete_image, name='delete-image'),

]
