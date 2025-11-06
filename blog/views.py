from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.contrib import messages
from django.db.models import Q
from django.views.generic import ListView
from .forms import PostForm, RegisterForm, CommentForm, UserUpdateForm, ProfileUpdateForm
from .models import Post, Tag, Category, Profile
from datetime import datetime
from rest_framework import generics
from .serializers import PostSerializer
from rest_framework.permissions import IsAuthenticatedOrReadOnly



class PostListAPI(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class PostDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer



def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # автоматический вход после регистрации
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'blog/register.html', {'form': form})



@login_required
def profile(request):
    user = request.user

    # Создаем профиль если его нет (защита от ошибки)
    profile_obj, created = Profile.objects.get_or_create(user=user)
   
    posts = user.posts.all()  # все посты, созданные пользователем

    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, '✅ Профиль успешно обновлён!')
            return redirect('profile')
        else:
            messages.error(request, '❌ Ошибка при обновлении профиля.')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form, 
        'p_form': p_form,
        'user': user, 
        'posts': posts,
        'profile': profile_obj,
        }
    return render(request, 'blog/profile.html',context)



@login_required
def edit_profile(request):
    # Создаем профиль если его нет
    profile_obj, created = Profile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile_obj)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=profile_obj)

    return render(request, 'blog/edit_profile.html', {
        'u_form': u_form,
        'p_form': p_form
    })



@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            # post.date = timezone.now()  # Текущая дата и время
            post.author = request.user  # сохраняем автора
            post.save()
            form.save_m2m()  # сохраняем теги ManyToMany
            messages.success(request, '🎉 Пост успешно создан!')
            messages.info(request, 'Не забудьте добавить теги')
            return redirect('post_detail', post_id=post.id)
    else:
        form = PostForm()
    return render(request, 'blog/create_post.html', {'form': form})



def post_detail(request, post_id):
    # Получаем пост и его комментарии
    post = get_object_or_404(Post, id=post_id)
    comments = post.comments.all().order_by('-created_at')  # 🔹 новые комментарии сверху

    # ЕСЛИ отправлен комментарий (POST запрос)
    if request.method == 'POST':
        # Проверяем авторизацию
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Обрабатываем форму комментария
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)  # создаем объект, но не сохраняем
            comment.post = post                # 🔹 привязываем к текущему посту
            comment.author = request.user      # 🔹 устанавливаем автора
            comment.save()                     # сохраняем в БД
            return redirect('post_detail', post_id=post.id)  # обновляем страницу
    
    # ЕСЛИ просто зашли на страницу (GET запрос)
    else:
        form = CommentForm()

    # Передаем все в шаблон
    return render(request, 'blog/post_detail.html', {
        'post': post,
        'comments': comments,
        'form': form
    })



def category_posts(request, slug):
    category = get_object_or_404(Category, slug=slug)
    posts = category.posts.all().order_by('-date')
    return render(request, 'blog/category_posts.html', {
        'category': category,
        'posts': posts
    })



@login_required
def edit_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        messages.error(request, '❌ Вы не можете редактировать этот пост!')
        return redirect('home')
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.date = timezone.now()
            post.save()
            messages.success(request, '✅ Пост успешно обновлён!')
            return redirect('post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)
    return render(request, 'blog/edit_post.html', {
        'form': form, 
        'post': post})



@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        messages.error(request, '❌ Вы не можете удалить этот пост!')
        return redirect('home')
    if request.method == 'POST':
        post_title = post.title
        post.delete()
        messages.warning(request, f'🗑️ Пост "{post_title}" был удалён.')
        return redirect('home')
    
    return render(request, 'blog/delete_post.html', {'post': post})



def posts_by_tag(request, slug):
    tag = get_object_or_404(Tag, slug=slug)
    posts = tag.posts.all().order_by('-date')  # 🔹 Магия related_name!
    return render(request, 'blog/posts_by_tag.html', {
        'tag': tag,
        'posts': posts})



class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
# def post_list(request):
#     post_list = Post.objects.all().order_by('-date')
#     paginator = Paginator(post_list, 5)  # 5 постов на страницу
#     page_number = request.GET.get('page')
#     page_obj = paginator.get_page(page_number)
#     return render(request, 'blog/post_list.html', {'page_obj': page_obj})




@login_required
def my_posts(request):
    # 🔹 Только посты текущего пользователя
    posts = request.user.posts.all().order_by('-date')
    
    # Пагинация
    paginator = Paginator(posts, 5)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'blog/my_posts.html', {
        'page_obj': page_obj,
        'posts_count': posts.count()
    })


def home(request):
    # 🔍 Поисковый запрос (должен быть ПЕРВЫМ!)
    query = request.GET.get('q')
    if query:
        posts = Post.objects.filter(
            Q(title__icontains=query) | Q(text__icontains=query)  # 🔹 исправлено content → text
        ).order_by('-date')

        # ✅ Сообщение только при поиске
        if posts.exists():
            messages.success(request, f'✅ Найдено {posts.count()} совпадений по запросу: "{query}"')
        else:
            messages.info(request, f'🔍 По запросу "{query}" ничего не найдено')

    else:
        posts = Post.objects.all().order_by('-date')
    # 📄 Пагинация
    paginator = Paginator(posts, 5)  # 5 постов на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)  # 🔹 автоматически обрабатывает page=9999

    # 📦 Контекст для шаблона
    context = {
        'name': 'Hoshgeldi',
        'date': datetime.now(),
        'categories': Category.objects.all(),
        'tags': Tag.objects.all(),
        'page_obj': page_obj,  # 🔹 используем page_obj вместо posts
        'query': query,  # 🔹 передаем поисковый запрос в шаблон
    }
    
    return render(request, 'blog/home.html', context)










from rest_framework import generics, permissions
from .models import Post, Category, Tag
from .serializers import PostSerializer, CategorySerializer, TagSerializer

# Посты
class PostListAPI(generics.ListCreateAPIView):
    queryset = Post.objects.all().order_by('-date')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

class PostDetailAPI(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

# Категории
class CategoryListAPI(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

class CategoryPostsAPI(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        slug = self.kwargs['slug']
        return Post.objects.filter(category__slug=slug)

# Теги
class TagListAPI(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer

class TagPostsAPI(generics.ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        slug = self.kwargs['slug']
        return Post.objects.filter(tags__slug=slug)
