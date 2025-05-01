from django.contrib import admin
from .models import Post, Category, Tag, Comment


class CommentInline(admin.StackedInline):
    model = Comment
    extra = 0



@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'category', 'created_at', 'views', 'is_visible')
    list_filter = ('is_visible', 'created_at', 'tags', 'category')
    search_fields = ('title', 'content', 'author_comment')
    ordering = ('-created_at',)
    list_editable = ('is_visible',)
    inlines = (CommentInline,)
    list_per_page = 15


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'content', 'created_at', 'is_verified')
    list_filter = ('user', 'post', 'created_at', 'is_verified')
    search_fields = ('post__title', 'content')
    ordering = ('-created_at',)
    list_editable = ('is_verified',)
    list_per_page = 15


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name', 'slug')

