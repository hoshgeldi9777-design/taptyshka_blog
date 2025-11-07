from django.urls import path
from . import views
from .views import (
    PostListAPI, PostDetailAPI, PostListView,
    CategoryListAPI, CategoryPostsAPI,
    TagListAPI, TagPostsAPI
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('', views.home, name='home'),
    path('new/', views.create_post, name='create_post'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('post/<int:post_id>/edit/', views.edit_post, name='edit_post'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('register/', views.register, name='register'),
    path('category/<slug:slug>/', views.category_posts, name='category_posts'),
    path('tag/<slug:slug>/', views.posts_by_tag, name='posts_by_tag'),
    path('profile/', views.profile, name='profile'),   # 🔹 личный кабинет
    path('profile/edit/', views.edit_profile, name='edit_profile'),  # 🔹 редактирование
    path('my_posts/', views.my_posts, name='my_posts'), 
    path('', PostListView.as_view(), name='post_list'),
    path('api/posts/', PostListAPI.as_view(), name='post_list_api'),
    path('api/posts/<int:pk>/', PostDetailAPI.as_view(), name='post_detail_api'),
     # Получение токена
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # Обновление токена
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
     # Авторизация
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Посты
    path('api/posts/', PostListAPI.as_view(), name='post_list_api'),
    path('api/posts/<int:pk>/', PostDetailAPI.as_view(), name='post_detail_api'),

    # Категории
    path('api/categories/', CategoryListAPI.as_view(), name='category_list_api'),
    path('api/categories/<slug:slug>/', CategoryPostsAPI.as_view(), name='category_posts_api'),

    # Теги
    path('api/tags/', TagListAPI.as_view(), name='tag_list_api'),
    path('api/tags/<slug:slug>/', TagPostsAPI.as_view(), name='tag_posts_api'),

    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
]