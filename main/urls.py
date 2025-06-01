# main/urls.py
from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('reviews/', views.reviews, name='reviews'),
    path('pricing/', views.pricing, name='pricing'),
    path('courses/', views.course_list, name='course_list'),
    path('course/<int:course_id>/', views.course_detail, name='course_detail'),
    path('course/<int:course_id>/load-next/<int:current_block_id>/', 
         views.load_next_content, name='load_next_content'),
    path('course/<int:course_id>/load-next/<int:current_block_id>/<int:current_subblock_id>/', 
         views.load_next_content, name='load_next_content_with_subblock'),
    path('course/<int:course_id>/load/<int:block_id>/', 
         views.load_content, name='load_content'),
    path('course/<int:course_id>/load/<int:block_id>/<int:subblock_id>/', 
         views.load_content, name='load_content_with_subblock'),
]