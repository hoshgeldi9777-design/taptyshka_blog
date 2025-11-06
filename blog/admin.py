from django.contrib import admin
from .models import Post, Category, Tag

# admin.site.register(Post)
# admin.site.register(Category)
# admin.site.register(Tag)

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}  # Автозаполнение slug из name


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}  # Автозаполнение slug из name

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'date']
    list_filter = ['category', 'date']
    filter_horizontal = ['tags']  # 🔹 Удобный виджет для выбора тегов


