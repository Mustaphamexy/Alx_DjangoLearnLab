from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
)
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django.http import JsonResponse, HttpResponseForbidden
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from .models import Post, Profile, Comment, Category, Tag

# Import only the forms we need
from .forms import (
    UserRegisterForm, UserUpdateForm, ProfileUpdateForm,
    PostForm, CommentForm, SearchForm, CustomAuthenticationForm,
    CommentUpdateForm, AdvancedSearchForm
)
# CommentDeleteForm is not needed as an import since it's a simple form
# We'll create it inline or remove the import

# Home View
class HomeView(ListView):
    """Home page showing latest posts"""
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    paginate_by = 6
    
    def get_queryset(self):
        return Post.objects.filter(status='published').select_related('author').prefetch_related('categories', 'tags')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_posts'] = Post.objects.filter(status='published').order_by('-views')[:3]
        context['categories'] = Category.objects.annotate(post_count=Count('posts')).order_by('-post_count')[:8]
        context['recent_posts'] = Post.objects.filter(status='published').order_by('-published_date')[:5]
        context['total_posts'] = Post.objects.filter(status='published').count()
        # Get popular tags
        context['popular_tags'] = Tag.objects.annotate(
            post_count=Count('posts')
        ).filter(post_count__gt=0).order_by('-post_count')[:10]
        # Get count of users with posts
        context['users'] = User.objects.filter(posts__isnull=False).distinct().count()
        return context

# Post List View
class PostListView(ListView):
    """View all blog posts with pagination"""
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 9
    ordering = ['-published_date']
    
    def get_queryset(self):
        queryset = Post.objects.filter(status='published').select_related('author').prefetch_related('categories', 'tags')
        
        # Filter by category if provided
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(Category, slug=category_slug)
            queryset = queryset.filter(categories=category)
        
        # Filter by tag if provided
        tag_slug = self.kwargs.get('tag_slug')
        if tag_slug:
            tag = get_object_or_404(Tag, slug=tag_slug)
            queryset = queryset.filter(tags=tag)
        
        # Search functionality
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query) |
                Q(excerpt__icontains=search_query) |
                Q(author__username__icontains=search_query) |
                Q(tags__name__icontains=search_query)
            ).distinct()
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_form'] = SearchForm(self.request.GET or None)
        context['categories'] = Category.objects.annotate(post_count=Count('posts')).order_by('-post_count')
        context['popular_tags'] = Tag.objects.annotate(
            post_count=Count('posts')
        ).filter(post_count__gt=0).order_by('-post_count')[:15]
        context['total_posts'] = Post.objects.filter(status='published').count()
        
        # Check if we're filtering by tag
        tag_slug = self.kwargs.get('tag_slug')
        if tag_slug:
            context['current_tag'] = get_object_or_404(Tag, slug=tag_slug)
        
        return context

# Post Detail View
class PostDetailView(DetailView):
    """View a single blog post with comments"""
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    
    def get_object(self):
        """Get post object and increment view count"""
        obj = super().get_object()
        obj.increment_views()
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comment_form'] = CommentForm()
        context['comments'] = self.object.comments.filter(is_active=True).select_related('author')
        context['related_posts'] = Post.objects.filter(
            tags__in=self.object.tags.all(),
            status='published'
        ).exclude(id=self.object.id).distinct()[:3]
        return context

# Create Post View
class PostCreateView(LoginRequiredMixin, CreateView):
    """Create a new blog post"""
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    success_url = reverse_lazy('post-list')
    
    def form_valid(self, form):
        """Set the author to current user and handle slug generation"""
        form.instance.author = self.request.user
        
        # Generate slug from title if not provided
        if not form.instance.slug:
            from django.utils.text import slugify
            form.instance.slug = slugify(form.instance.title)
        
        messages.success(self.request, 'Your post has been created successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Create New Post'
        context['submit_text'] = 'Create Post'
        return context

# Update Post View
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing blog post"""
    model = Post
    form_class = PostForm
    template_name = 'blog/post_form.html'
    
    def test_func(self):
        """Check if user is the author of the post"""
        post = self.get_object()
        return self.request.user == post.author
    
    def handle_no_permission(self):
        """Handle unauthorized access"""
        messages.error(self.request, 'You are not authorized to edit this post.')
        return redirect('post-detail', slug=self.get_object().slug)
    
    def form_valid(self, form):
        """Update the post and show success message"""
        form.instance.updated_date = timezone.now()
        messages.success(self.request, 'Your post has been updated successfully!')
        return super().form_valid(form)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Update Post'
        context['submit_text'] = 'Update Post'
        return context

# Delete Post View
class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a blog post"""
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('post-list')
    
    def test_func(self):
        """Check if user is the author of the post"""
        post = self.get_object()
        return self.request.user == post.author
    
    def handle_no_permission(self):
        """Handle unauthorized access"""
        messages.error(self.request, 'You are not authorized to delete this post.')
        return redirect('post-detail', slug=self.get_object().slug)
    
    def delete(self, request, *args, **kwargs):
        """Show success message after deletion"""
        messages.success(request, 'Your post has been deleted successfully!')
        return super().delete(request, *args, **kwargs)

# User Posts View
class UserPostListView(LoginRequiredMixin, ListView):
    """View all posts by the logged-in user"""
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        return Post.objects.filter(author=self.request.user).order_by('-published_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['total_posts'] = Post.objects.filter(author=self.request.user).count()
        context['published_posts'] = Post.objects.filter(author=self.request.user, status='published').count()
        context['draft_posts'] = Post.objects.filter(author=self.request.user, status='draft').count()
        return context

# Category Posts View
class CategoryPostListView(ListView):
    """View all posts in a specific category"""
    model = Post
    template_name = 'blog/category_posts.html'
    context_object_name = 'posts'
    paginate_by = 9
    
    def get_queryset(self):
        self.category = get_object_or_404(Category, slug=self.kwargs.get('slug'))
        return Post.objects.filter(categories=self.category, status='published').order_by('-published_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['categories'] = Category.objects.annotate(post_count=Count('posts')).order_by('-post_count')
        return context

# Tag Posts View
class TagPostListView(ListView):
    """View all posts with a specific tag"""
    model = Post
    template_name = 'blog/tag_posts.html'
    context_object_name = 'posts'
    paginate_by = 9
    
    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs.get('slug'))
        return Post.objects.filter(tags=self.tag, status='published').order_by('-published_date')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        context['popular_tags'] = Tag.objects.annotate(
            post_count=Count('posts')
        ).filter(post_count__gt=0).order_by('-post_count')[:15]
        return context

# Comment Views
class CommentCreateView(LoginRequiredMixin, CreateView):
    """Add a comment to a post"""
    model = Comment
    form_class = CommentForm
    
    def form_valid(self, form):
        """Set post and author for the comment"""
        post = get_object_or_404(Post, slug=self.kwargs.get('slug'))
        form.instance.post = post
        form.instance.author = self.request.user
        messages.success(self.request, 'Your comment has been added!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('post-detail', kwargs={'slug': self.kwargs.get('slug')}) + '#comments'

class CommentUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    """Update an existing comment"""
    model = Comment
    form_class = CommentUpdateForm
    template_name = 'blog/comment_form.html'
    
    def test_func(self):
        """Check if user is the author of the comment"""
        comment = self.get_object()
        return self.request.user == comment.author
    
    def handle_no_permission(self):
        """Handle unauthorized access"""
        messages.error(self.request, 'You are not authorized to edit this comment.')
        return redirect('post-detail', slug=self.get_object().post.slug)
    
    def form_valid(self, form):
        """Update the comment and show success message"""
        form.instance.updated_date = timezone.now()
        messages.success(self.request, 'Your comment has been updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('post-detail', kwargs={'slug': self.object.post.slug}) + f'#comment-{self.object.id}'

class CommentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """Delete a comment"""
    model = Comment
    template_name = 'blog/comment_confirm_delete.html'
    
    def test_func(self):
        """Check if user is the author of the comment or post author"""
        comment = self.get_object()
        return self.request.user == comment.author or self.request.user == comment.post.author
    
    def handle_no_permission(self):
        """Handle unauthorized access"""
        messages.error(self.request, 'You are not authorized to delete this comment.')
        return redirect('post-detail', slug=self.get_object().post.slug)
    
    def delete(self, request, *args, **kwargs):
        """Show success message after deletion"""
        comment = self.get_object()
        post_slug = comment.post.slug
        messages.success(request, 'Comment has been deleted successfully!')
        response = super().delete(request, *args, **kwargs)
        return redirect('post-detail', slug=post_slug) + '#comments'

# Function-based views for authentication
def user_login(request):
    """Login view"""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    
    context = {
        'form': form,
        'title': 'Login'
    }
    return render(request, 'blog/login.html', context)

def user_logout(request):
    """Logout view"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

def register(request):
    """Register view"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    
    context = {
        'form': form,
        'title': 'Register'
    }
    return render(request, 'blog/register.html', context)

@login_required
def profile(request):
    """Profile view and update"""
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(
            request.POST, 
            request.FILES, 
            instance=request.user.profile
        )
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form,
        'title': 'Profile'
    }
    return render(request, 'blog/profile.html', context)

# API-like views for AJAX
@login_required
def like_post(request, slug):
    """Like/unlike a post (simplified version)"""
    post = get_object_or_404(Post, slug=slug)
    
    if request.method == 'POST' and request.is_ajax():
        # In a real implementation, you'd have a Like model
        # This is a simplified version
        return JsonResponse({'success': True, 'message': 'Post liked!'})
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

# Enhanced Search View
def search_posts(request):
    """Search posts with advanced filtering"""
    form = AdvancedSearchForm(request.GET or None)
    posts = Post.objects.filter(status='published').select_related('author').prefetch_related('categories', 'tags')
    
    if form.is_valid():
        query = form.cleaned_data.get('query')
        category = form.cleaned_data.get('category')
        tag = form.cleaned_data.get('tag')
        author = form.cleaned_data.get('author')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        status = form.cleaned_data.get('status')
        
        # Apply filters
        if query:
            posts = posts.filter(
                Q(title__icontains=query) |
                Q(content__icontains=query) |
                Q(excerpt__icontains=query) |
                Q(author__username__icontains=query) |
                Q(tags__name__icontains=query)
            ).distinct()
        
        if category:
            posts = posts.filter(categories=category)
        
        if tag:
            posts = posts.filter(tags=tag)
        
        if author:
            posts = posts.filter(author=author)
        
        if date_from:
            posts = posts.filter(published_date__date__gte=date_from)
        
        if date_to:
            posts = posts.filter(published_date__date__lte=date_to)
        
        if status:
            posts = posts.filter(status=status)
    
    # Get popular tags for sidebar
    popular_tags = Tag.objects.annotate(
        post_count=Count('posts')
    ).filter(post_count__gt=0).order_by('-post_count')[:15]
    
    # Get recent posts for sidebar
    recent_posts = Post.objects.filter(status='published').order_by('-published_date')[:5]
    
    # Pagination
    paginator = Paginator(posts, 9)
    page = request.GET.get('page')
    
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    
    context = {
        'form': form,
        'posts': posts,
        'title': 'Search Results',
        'query': request.GET.get('query', ''),
        'popular_tags': popular_tags,
        'recent_posts': recent_posts,
        'total_results': paginator.count,
    }
    return render(request, 'blog/search_results.html', context)

# AJAX Comment Views
@login_required
def comment_like(request, comment_id):
    """Like a comment (AJAX)"""
    comment = get_object_or_404(Comment, id=comment_id)
    
    if request.method == 'POST' and request.is_ajax():
        # Simple like toggle - in production, use a Like model
        return JsonResponse({
            'success': True, 
            'message': 'Comment liked!'
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def comment_reply(request, comment_id):
    """Reply to a comment (AJAX)"""
    parent_comment = get_object_or_404(Comment, id=comment_id)
    
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = parent_comment.post
            comment.author = request.user
            comment.save()
            messages.success(request, 'Your reply has been added!')
            return redirect('post-detail', slug=parent_comment.post.slug) + f'#comment-{comment.id}'
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})

# Tag cloud view
def tag_cloud(request):
    """Display all tags in a cloud format"""
    tags = Tag.objects.annotate(
        post_count=Count('posts')
    ).filter(post_count__gt=0).order_by('name')
    
    # Calculate font sizes for tag cloud
    if tags:
        max_count = max(tag.post_count for tag in tags)
        min_count = min(tag.post_count for tag in tags)
        
        for tag in tags:
            # Normalize count to a scale of 1-5 for font sizes
            if max_count > min_count:
                normalized = (tag.post_count - min_count) / (max_count - min_count)
                tag.font_size = 1 + (normalized * 4)  # Scale to 1-5
            else:
                tag.font_size = 3  # Default size if all counts are equal
    
    context = {
        'tags': tags,
        'title': 'Tag Cloud',
    }
    return render(request, 'blog/tag_cloud.html', context)