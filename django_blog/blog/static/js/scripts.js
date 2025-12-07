// Enhanced JavaScript for authentication system
document.addEventListener('DOMContentLoaded', function() {
    console.log('Blog authentication system loaded');
    
    // Form validation enhancement
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
                submitBtn.disabled = true;
            }
        });
    });
    
    // Password visibility toggle
    const passwordToggles = document.querySelectorAll('.password-toggle');
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const input = this.previousElementSibling;
            const type = input.getAttribute('type') === 'password' ? 'text' : 'password';
            input.setAttribute('type', type);
            this.classList.toggle('fa-eye');
            this.classList.toggle('fa-eye-slash');
        });
    });
    
    // Profile picture preview
    const profilePicInput = document.getElementById('id_profile_picture');
    if (profilePicInput) {
        profilePicInput.addEventListener('change', function(e) {
            const file = this.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    const preview = document.querySelector('.profile-picture img') || 
                                   document.querySelector('.profile-picture-default');
                    if (preview) {
                        if (preview.tagName === 'IMG') {
                            preview.src = e.target.result;
                        } else {
                            const img = document.createElement('img');
                            img.src = e.target.result;
                            img.alt = 'Profile preview';
                            preview.parentElement.innerHTML = '';
                            preview.parentElement.appendChild(img);
                        }
                    }
                }
                reader.readAsDataURL(file);
            }
        });
    }
    
    // Auto-hide messages after 5 seconds
    const messages = document.querySelectorAll('.alert');
    messages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transform = 'translateY(-20px)';
            setTimeout(() => {
                message.style.display = 'none';
            }, 300);
        }, 5000);
    });
    
    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            if (targetId !== '#') {
                const targetElement = document.querySelector(targetId);
                if (targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop - 100,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
    
    // Form field focus effects
    const formInputs = document.querySelectorAll('.form-control');
    formInputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            if (!this.value) {
                this.parentElement.classList.remove('focused');
            }
        });
        
        // Add floating label effect
        if (this.value) {
            this.parentElement.classList.add('focused');
        }
    });
    
    // Enhanced JavaScript for CRUD operations
    console.log('Blog CRUD system loaded');
    
    // Post Form Character Counters
    const titleInput = document.getElementById('id_title');
    const contentTextarea = document.getElementById('id_content');
    const excerptTextarea = document.getElementById('id_excerpt');
    
    if (titleInput) {
        titleInput.addEventListener('input', updateTitleCounter);
        updateTitleCounter();
    }
    
    if (contentTextarea) {
        contentTextarea.addEventListener('input', updateContentCounter);
        updateContentCounter();
    }
    
    if (excerptTextarea) {
        excerptTextarea.addEventListener('input', updateExcerptCounter);
        updateExcerptCounter();
    }
    
    function updateTitleCounter() {
        const counter = getOrCreateCounter(titleInput, 'title-counter');
        const count = titleInput.value.length;
        counter.textContent = `${count} characters`;
        counter.className = `char-counter ${count >= 10 ? 'valid' : 'invalid'}`;
    }
    
    function updateContentCounter() {
        const counter = getOrCreateCounter(contentTextarea, 'content-counter');
        const count = contentTextarea.value.length;
        const wordCount = contentTextarea.value.trim().split(/\s+/).length;
        counter.textContent = `${count} characters, ${wordCount} words`;
        counter.className = `char-counter ${count >= 50 ? 'valid' : 'invalid'}`;
    }
    
    function updateExcerptCounter() {
        const counter = getOrCreateCounter(excerptTextarea, 'excerpt-counter');
        const count = excerptTextarea.value.length;
        counter.textContent = `${count}/300 characters`;
        counter.className = `char-counter ${count <= 300 ? 'valid' : 'invalid'}`;
        
        if (count > 300) {
            excerptTextarea.value = excerptTextarea.value.substring(0, 300);
            updateExcerptCounter();
        }
    }
    
    function getOrCreateCounter(element, id) {
        let counter = document.getElementById(id);
        if (!counter) {
            counter = document.createElement('div');
            counter.id = id;
            counter.className = 'char-counter';
            element.parentNode.insertBefore(counter, element.nextSibling);
        }
        return counter;
    }
    
    // Image Preview for Featured Image
    const featuredImageInput = document.getElementById('id_featured_image');
    if (featuredImageInput) {
        featuredImageInput.addEventListener('change', function(e) {
            const file = this.files[0];
            if (file) {
                // Validate file type
                const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
                if (!validTypes.includes(file.type)) {
                    alert('Please select a valid image file (JPEG, PNG, GIF, WebP).');
                    this.value = '';
                    return;
                }
                
                // Validate file size (max 5MB)
                if (file.size > 5 * 1024 * 1024) {
                    alert('Image size must be less than 5MB.');
                    this.value = '';
                    return;
                }
                
                // Create preview
                const reader = new FileReader();
                reader.onload = function(e) {
                    let preview = document.querySelector('.image-preview');
                    if (!preview) {
                        preview = document.createElement('div');
                        preview.className = 'image-preview';
                        featuredImageInput.parentNode.insertBefore(preview, featuredImageInput.nextSibling);
                    }
                    preview.innerHTML = `
                        <img src="${e.target.result}" alt="Preview" style="max-width: 200px; border-radius: 8px;">
                        <button type="button" class="btn-remove-preview">
                            <i class="fas fa-times"></i>
                        </button>
                    `;
                    
                    // Add remove button functionality
                    const removeBtn = preview.querySelector('.btn-remove-preview');
                    removeBtn.addEventListener('click', function() {
                        featuredImageInput.value = '';
                        preview.remove();
                    });
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    // Auto-save draft functionality
    let autoSaveInterval;
    const postForm = document.querySelector('.post-form');
    
    if (postForm && (window.location.pathname.includes('/create') || window.location.pathname.includes('/update'))) {
        autoSaveInterval = setInterval(autoSaveDraft, 30000); // Auto-save every 30 seconds
        
        // Save on form submit
        postForm.addEventListener('submit', function() {
            clearInterval(autoSaveInterval);
            localStorage.removeItem('draftPost');
            showNotification('Post saved!', 'success');
        });
        
        // Load draft if exists
        loadDraft();
        
        // Save on page unload
        window.addEventListener('beforeunload', function(e) {
            if (postFormHasContent()) {
                e.preventDefault();
                e.returnValue = 'You have unsaved changes. Are you sure you want to leave?';
            }
        });
    }
    
    function autoSaveDraft() {
        if (postFormHasContent()) {
            const draft = {
                title: titleInput ? titleInput.value : '',
                content: contentTextarea ? contentTextarea.value : '',
                excerpt: excerptTextarea ? excerptTextarea.value : '',
                status: document.getElementById('id_status') ? document.getElementById('id_status').value : 'draft',
                tags_input: tagInput ? tagInput.value : '',
                timestamp: new Date().toISOString()
            };
            
            localStorage.setItem('draftPost', JSON.stringify(draft));
            showNotification('Draft auto-saved', 'info');
        }
    }
    
    function loadDraft() {
        const draft = localStorage.getItem('draftPost');
        if (draft) {
            const draftData = JSON.parse(draft);
            const shouldLoad = confirm('You have a saved draft from ' + 
                new Date(draftData.timestamp).toLocaleTimeString() + 
                '. Would you like to load it?');
            
            if (shouldLoad) {
                if (titleInput) titleInput.value = draftData.title;
                if (contentTextarea) contentTextarea.value = draftData.content;
                if (excerptTextarea) excerptTextarea.value = draftData.excerpt;
                if (document.getElementById('id_status')) {
                    document.getElementById('id_status').value = draftData.status;
                }
                if (tagInput && draftData.tags_input) {
                    tagInput.value = draftData.tags_input;
                    updateTagCounter();
                }
                updateTitleCounter();
                updateContentCounter();
                updateExcerptCounter();
                showNotification('Draft loaded', 'success');
            } else {
                localStorage.removeItem('draftPost');
            }
        }
    }
    
    function postFormHasContent() {
        return (titleInput && titleInput.value.trim().length > 0) ||
               (contentTextarea && contentTextarea.value.trim().length > 0);
    }
    
    // Delete confirmation enhancement
    const deleteButtons = document.querySelectorAll('.btn-delete');
    deleteButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this post? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
    
    // Rich text editor simulation (basic)
    if (contentTextarea) {
        // Add toolbar
        const toolbar = createTextEditorToolbar(contentTextarea);
        contentTextarea.parentNode.insertBefore(toolbar, contentTextarea);
    }
    
    function createTextEditorToolbar(textarea) {
        const toolbar = document.createElement('div');
        toolbar.className = 'text-editor-toolbar';
        toolbar.innerHTML = `
            <div class="btn-group">
                <button type="button" class="btn-format" data-format="bold"><i class="fas fa-bold"></i></button>
                <button type="button" class="btn-format" data-format="italic"><i class="fas fa-italic"></i></button>
                <button type="button" class="btn-format" data-format="underline"><i class="fas fa-underline"></i></button>
            </div>
            <div class="btn-group">
                <button type="button" class="btn-format" data-format="h2"><i class="fas fa-heading"></i> H2</button>
                <button type="button" class="btn-format" data-format="h3"><i class="fas fa-heading"></i> H3</button>
            </div>
            <div class="btn-group">
                <button type="button" class="btn-format" data-format="link"><i class="fas fa-link"></i></button>
                <button type="button" class="btn-format" data-format="code"><i class="fas fa-code"></i></button>
                <button type="button" class="btn-format" data-format="quote"><i class="fas fa-quote-right"></i></button>
            </div>
        `;
        
        // Add event listeners to format buttons
        toolbar.querySelectorAll('.btn-format').forEach(button => {
            button.addEventListener('click', function() {
                const format = this.dataset.format;
                applyFormat(textarea, format);
            });
        });
        
        return toolbar;
    }
    
    function applyFormat(textarea, format) {
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const selectedText = textarea.value.substring(start, end);
        let formattedText = '';
        
        switch(format) {
            case 'bold':
                formattedText = `**${selectedText}**`;
                break;
            case 'italic':
                formattedText = `*${selectedText}*`;
                break;
            case 'underline':
                formattedText = `<u>${selectedText}</u>`;
                break;
            case 'h2':
                formattedText = `\n## ${selectedText}\n`;
                break;
            case 'h3':
                formattedText = `\n### ${selectedText}\n`;
                break;
            case 'link':
                const url = prompt('Enter URL:');
                if (url) {
                    formattedText = `[${selectedText}](${url})`;
                } else {
                    return;
                }
                break;
            case 'code':
                formattedText = `\`${selectedText}\``;
                break;
            case 'quote':
                formattedText = `> ${selectedText}`;
                break;
        }
        
        textarea.value = textarea.value.substring(0, start) + formattedText + textarea.value.substring(end);
        textarea.focus();
        textarea.selectionStart = textarea.selectionEnd = start + formattedText.length;
        updateContentCounter();
    }
    
    // Reading time calculation
    function calculateReadingTime(text) {
        const wordsPerMinute = 200;
        const words = text.trim().split(/\s+/).length;
        const minutes = Math.ceil(words / wordsPerMinute);
        return minutes;
    }
    
    // Show notification
    function showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <span>${message}</span>
            <button type="button" class="btn-close-notification">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        document.body.appendChild(notification);
        
        // Add close button functionality
        notification.querySelector('.btn-close-notification').addEventListener('click', function() {
            notification.remove();
        });
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (notification.parentNode) {
                notification.remove();
            }
        }, 5000);
    }
    
    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-tooltip]');
    tooltips.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
    
    function showTooltip(e) {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = this.dataset.tooltip;
        document.body.appendChild(tooltip);
        
        const rect = this.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
        
        this._tooltip = tooltip;
    }
    
    function hideTooltip() {
        if (this._tooltip) {
            this._tooltip.remove();
            this._tooltip = null;
        }
    }
    
    // Tag input functionality
    const tagInput = document.querySelector('input[data-role="tagsinput"]');
    if (tagInput) {
        // Initialize tag input
        initializeTagInput(tagInput);
        
        // Add character counter for tags
        const tagCounter = document.createElement('div');
        tagCounter.className = 'tag-counter';
        tagCounter.id = 'tag-counter';
        tagInput.parentNode.insertBefore(tagCounter, tagInput.nextSibling);
        
        function updateTagCounter() {
            const tags = tagInput.value.split(',').filter(tag => tag.trim());
            const count = tags.length;
            tagCounter.textContent = `${count}/10 tags`;
            tagCounter.className = `tag-counter ${count <= 10 ? 'valid' : 'invalid'}`;
            
            if (count > 10) {
                // Remove extra tags
                const validTags = tags.slice(0, 10);
                tagInput.value = validTags.join(', ');
                updateTagCounter();
            }
        }
        
        tagInput.addEventListener('input', updateTagCounter);
        updateTagCounter();
    }
    
    // Function to initialize tag input
    function initializeTagInput(input) {
        input.addEventListener('keydown', function(e) {
            if (e.key === 'Enter' || e.key === ',') {
                e.preventDefault();
                const value = this.value.trim();
                if (value) {
                    const tags = this.value.split(',').map(tag => tag.trim()).filter(tag => tag);
                    // Remove duplicates
                    const uniqueTags = [...new Set(tags)];
                    this.value = uniqueTags.join(', ') + ', ';
                    updateTagCounter();
                }
            }
        });
        
        // Auto-complete functionality
        const availableTags = JSON.parse(document.getElementById('available-tags')?.textContent || '[]');
        if (availableTags.length > 0) {
            input.addEventListener('input', function() {
                const currentValue = this.value;
                const lastTag = currentValue.split(',').pop().trim();
                
                if (lastTag.length > 0) {
                    // Filter matching tags
                    const matches = availableTags.filter(tag => 
                        tag.toLowerCase().includes(lastTag.toLowerCase())
                    );
                    
                    // Show suggestions
                    showTagSuggestions(matches, lastTag, this);
                } else {
                    // Remove suggestions if input is empty
                    const existingSuggestions = document.querySelector('.tag-suggestions');
                    if (existingSuggestions) {
                        existingSuggestions.remove();
                    }
                }
            });
            
            // Close suggestions when clicking outside
            document.addEventListener('click', function(e) {
                if (!e.target.closest('.tag-suggestions') && !e.target.closest('input[data-role="tagsinput"]')) {
                    const suggestions = document.querySelector('.tag-suggestions');
                    if (suggestions) {
                        suggestions.remove();
                    }
                }
            });
        }
    }
    
    function showTagSuggestions(matches, currentInput, inputElement) {
        // Remove existing suggestions
        const existingSuggestions = document.querySelector('.tag-suggestions');
        if (existingSuggestions) {
            existingSuggestions.remove();
        }
        
        if (matches.length > 0) {
            const suggestions = document.createElement('div');
            suggestions.className = 'tag-suggestions';
            
            // Limit to 5 suggestions
            const limitedMatches = matches.slice(0, 5);
            
            limitedMatches.forEach(tag => {
                const suggestion = document.createElement('div');
                suggestion.className = 'tag-suggestion';
                suggestion.innerHTML = `
                    <i class="fas fa-tag"></i>
                    <span>${tag}</span>
                `;
                suggestion.addEventListener('click', function() {
                    const currentTags = inputElement.value.split(',').map(t => t.trim()).filter(t => t);
                    // Replace the last incomplete tag with the selected suggestion
                    currentTags[currentTags.length - 1] = tag;
                    inputElement.value = currentTags.join(', ') + ', ';
                    suggestions.remove();
                    updateTagCounter();
                    inputElement.focus();
                });
                suggestions.appendChild(suggestion);
            });
            
            inputElement.parentNode.appendChild(suggestions);
        }
    }
    
    // Add CSS for tag suggestions
    const style = document.createElement('style');
    style.textContent = `
        .tag-counter {
            font-size: 12px;
            margin-top: 5px;
            padding: 5px 10px;
            border-radius: 4px;
            display: inline-block;
        }
        
        .tag-counter.valid {
            background: #d4edda;
            color: #155724;
        }
        
        .tag-counter.invalid {
            background: #f8d7da;
            color: #721c24;
        }
        
        .tag-suggestions {
            position: absolute;
            background: white;
            border: 1px solid #ddd;
            border-radius: 4px;
            max-height: 200px;
            overflow-y: auto;
            z-index: 1000;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            width: 100%;
            margin-top: 5px;
        }
        
        .tag-suggestion {
            padding: 8px 12px;
            cursor: pointer;
            transition: background 0.3s;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .tag-suggestion:hover {
            background: #f8f9fa;
        }
        
        .tag-suggestion i {
            color: #42b883;
        }
    `;
    document.head.appendChild(style);
    
    // Comment system enhancements
    console.log('Blog comment system loaded');
    
    // Comment form enhancements
    const commentForm = document.querySelector('.comment-form');
    if (commentForm) {
        commentForm.addEventListener('submit', function(e) {
            const textarea = this.querySelector('textarea');
            if (textarea.value.trim().length < 5) {
                e.preventDefault();
                alert('Comment must be at least 5 characters long.');
                return false;
            }
            
            if (textarea.value.trim().length > 1000) {
                e.preventDefault();
                alert('Comment must be less than 1000 characters.');
                return false;
            }
            
            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Posting...';
                submitBtn.disabled = true;
            }
        });
    }
    
    // Real-time comment validation
    const commentTextarea = document.getElementById('comment-content');
    if (commentTextarea) {
        commentTextarea.addEventListener('input', function() {
            const length = this.value.trim().length;
            const submitBtn = document.querySelector('.comment-form button[type="submit"]');
            
            if (length < 5 || length > 1000) {
                this.style.borderColor = '#dc3545';
                if (submitBtn) submitBtn.disabled = true;
            } else {
                this.style.borderColor = '#28a745';
                if (submitBtn) submitBtn.disabled = false;
            }
        });
    }
    
    // Comment dropdown functionality
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.comment-actions')) {
            document.querySelectorAll('.dropdown-menu').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });
    
    // Comment like functionality
    document.querySelectorAll('.btn-reaction[data-action="like"]').forEach(btn => {
        btn.addEventListener('click', function() {
            const commentId = this.dataset.commentId;
            
            // Toggle UI
            const icon = this.querySelector('i');
            const countSpan = this.querySelector('.reaction-count');
            let count = parseInt(countSpan.textContent || 0);
            
            if (icon.classList.contains('far')) {
                // Like
                icon.classList.remove('far');
                icon.classList.add('fas');
                this.style.color = '#667eea';
                countSpan.textContent = count + 1;
                
                // Send AJAX request
                fetch(`/comments/${commentId}/like/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({action: 'like'})
                })
                .then(response => response.json())
                .then(data => {
                    if (!data.success) {
                        // Revert on error
                        icon.classList.remove('fas');
                        icon.classList.add('far');
                        this.style.color = '#666';
                        countSpan.textContent = count;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    // Revert on error
                    icon.classList.remove('fas');
                    icon.classList.add('far');
                    this.style.color = '#666';
                    countSpan.textContent = count;
                });
            } else {
                // Unlike
                icon.classList.remove('fas');
                icon.classList.add('far');
                this.style.color = '#666';
                countSpan.textContent = count - 1;
                
                // Send AJAX request
                fetch(`/comments/${commentId}/like/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': getCookie('csrftoken'),
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({action: 'unlike'})
                })
                .then(response => response.json())
                .then(data => {
                    if (!data.success) {
                        // Revert on error
                        icon.classList.remove('far');
                        icon.classList.add('fas');
                        this.style.color = '#667eea';
                        countSpan.textContent = count;
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    // Revert on error
                    icon.classList.remove('far');
                    icon.classList.add('fas');
                    this.style.color = '#667eea';
                    countSpan.textContent = count;
                });
            }
        });
    });
    
    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    // Smooth scroll to comment section
    const commentLinks = document.querySelectorAll('a[href*="#comments"]');
    commentLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId.includes('#comments')) {
                e.preventDefault();
                const targetElement = document.querySelector('#comments');
                if (targetElement) {
                    window.scrollTo({
                        top: targetElement.offsetTop - 100,
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
    
    // Auto-expand textarea on focus
    const textareas = document.querySelectorAll('textarea[id^="comment"]');
    textareas.forEach(textarea => {
        textarea.addEventListener('focus', function() {
            this.style.minHeight = '150px';
        });
        
        textarea.addEventListener('blur', function() {
            if (this.value.trim() === '') {
                this.style.minHeight = '';
            }
        });
    });
    
    // Comment reply functionality
    document.querySelectorAll('.btn-reply').forEach(btn => {
        btn.addEventListener('click', function() {
            const commentId = this.dataset.commentId;
            const commentElement = document.getElementById(`comment-${commentId}`);
            
            // Create reply form if it doesn't exist
            let replyForm = commentElement.querySelector('.reply-form');
            if (!replyForm) {
                replyForm = document.createElement('div');
                replyForm.className = 'reply-form mt-3';
                replyForm.innerHTML = `
                    <form method="post" action="/comments/${commentId}/reply/" class="comment-reply-form">
                        <input type="hidden" name="parent" value="${commentId}">
                        <div class="form-group">
                            <textarea name="content" class="form-control" placeholder="Write your reply..." rows="3" required></textarea>
                        </div>
                        <div class="form-group mb-0">
                            <button type="submit" class="btn btn-primary btn-sm">Post Reply</button>
                            <button type="button" class="btn btn-secondary btn-sm btn-cancel-reply">Cancel</button>
                        </div>
                    </form>
                `;
                
                commentElement.appendChild(replyForm);
                
                // Focus on textarea
                const textarea = replyForm.querySelector('textarea');
                textarea.focus();
                
                // Add cancel functionality
                replyForm.querySelector('.btn-cancel-reply').addEventListener('click', function() {
                    replyForm.remove();
                });
                
                // Add form submission handler
                const form = replyForm.querySelector('form');
                form.addEventListener('submit', function(e) {
                    const textarea = this.querySelector('textarea');
                    if (textarea.value.trim().length < 5) {
                        e.preventDefault();
                        alert('Reply must be at least 5 characters long.');
                        return false;
                    }
                    
                    if (textarea.value.trim().length > 1000) {
                        e.preventDefault();
                        alert('Reply must be less than 1000 characters.');
                        return false;
                    }
                    
                    // Show loading state
                    const submitBtn = this.querySelector('button[type="submit"]');
                    if (submitBtn) {
                        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Posting...';
                        submitBtn.disabled = true;
                    }
                });
            } else {
                // Toggle visibility
                replyForm.style.display = replyForm.style.display === 'none' ? 'block' : 'none';
                if (replyForm.style.display === 'block') {
                    replyForm.querySelector('textarea').focus();
                }
            }
        });
    });
    
    // Edit comment functionality
    document.querySelectorAll('.btn-edit-comment').forEach(btn => {
        btn.addEventListener('click', function() {
            const commentId = this.dataset.commentId;
            const commentElement = document.getElementById(`comment-${commentId}`);
            const contentElement = commentElement.querySelector('.comment-content');
            const originalContent = contentElement.textContent.trim();
            
            // Replace with edit form
            const editForm = document.createElement('div');
            editForm.className = 'comment-edit-form';
            editForm.innerHTML = `
                <form method="post" action="/comments/${commentId}/update/" class="mb-3">
                    <div class="form-group">
                        <textarea name="content" class="form-control" rows="4" required>${originalContent}</textarea>
                    </div>
                    <div class="form-group mb-0">
                        <button type="submit" class="btn btn-primary btn-sm">Update</button>
                        <button type="button" class="btn btn-secondary btn-sm btn-cancel-edit">Cancel</button>
                    </div>
                </form>
            `;
            
            contentElement.style.display = 'none';
            contentElement.parentNode.insertBefore(editForm, contentElement);
            
            // Focus on textarea
            const textarea = editForm.querySelector('textarea');
            textarea.focus();
            
            // Add cancel functionality
            editForm.querySelector('.btn-cancel-edit').addEventListener('click', function() {
                editForm.remove();
                contentElement.style.display = 'block';
            });
            
            // Add form submission handler
            const form = editForm.querySelector('form');
            form.addEventListener('submit', function(e) {
                const textarea = this.querySelector('textarea');
                if (textarea.value.trim().length < 5) {
                    e.preventDefault();
                    alert('Comment must be at least 5 characters long.');
                    return false;
                }
                
                if (textarea.value.trim().length > 1000) {
                    e.preventDefault();
                    alert('Comment must be less than 1000 characters.');
                    return false;
                }
                
                // Show loading state
                const submitBtn = this.querySelector('button[type="submit"]');
                if (submitBtn) {
                    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Updating...';
                    submitBtn.disabled = true;
                }
            });
        });
    });
    
    // Delete comment confirmation
    document.querySelectorAll('.btn-delete-comment').forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (!confirm('Are you sure you want to delete this comment? This action cannot be undone.')) {
                e.preventDefault();
            }
        });
    });
});