# posts/admin.py

from django.contrib import admin
from .models import Post, Comment

class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    readonly_fields = ['created_at', 'updated_at']

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at', 'like_count', 'comment_count']
    list_filter = ['created_at', 'author']
    search_fields = ['title', 'content', 'author__username']
    readonly_fields = ['created_at', 'updated_at']
    inlines = [CommentInline]
    
    def like_count(self, obj):
        return obj.like_count
    like_count.short_description = 'Likes'
    
    def comment_count(self, obj):
        return obj.comment_count
    comment_count.short_description = 'Comments'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'created_at', 'like_count']
    list_filter = ['created_at', 'author']
    search_fields = ['content', 'author__username', 'post__title']
    readonly_fields = ['created_at', 'updated_at']
    
    def like_count(self, obj):
        return obj.like_count
    like_count.short_description = 'Likes'