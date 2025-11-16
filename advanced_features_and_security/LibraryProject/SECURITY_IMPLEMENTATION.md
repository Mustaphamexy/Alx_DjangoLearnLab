# Security Implementation Documentation

## HTTPS Configuration

### Django Settings
- **SECURE_SSL_REDIRECT**: Redirects all HTTP traffic to HTTPS
- **SECURE_HSTS_SECONDS**: 1-year HSTS policy
- **SECURE_HSTS_INCLUDE_SUBDOMAINS**: Applies to all subdomains
- **SECURE_HSTS_PRELOAD**: Allows HSTS preloading

### Secure Cookies
- **SESSION_COOKIE_SECURE**: Session cookies only over HTTPS
- **CSRF_COOKIE_SECURE**: CSRF cookies only over HTTPS
- **SESSION_COOKIE_HTTPONLY**: Prevents JavaScript access to session cookies

### Security Headers
- **X_FRAME_OPTIONS**: DENY - Prevents clickjacking
- **SECURE_CONTENT_TYPE_NOSNIFF**: Prevents MIME sniffing
- **SECURE_BROWSER_XSS_FILTER**: Enables browser XSS protection
- **SECURE_REFERRER_POLICY**: same-origin - Limits referrer information

## Content Security Policy (CSP)

Implemented using django-csp to prevent XSS attacks:
- Default source restricted to self
- No external scripts allowed
- Inline styles allowed for Django admin compatibility
- No object embedding
- Frame ancestors denied

## Deployment Security

### Nginx Configuration
- HTTP to HTTPS redirect
- Modern TLS protocols (TLSv1.2, TLSv1.3)
- Security headers enforcement
- Static file caching with security headers
- Hidden file protection

### Environment Variables
Required for production:
```bash
DJANGO_SECRET_KEY=your_secure_secret_key
DJANGO_DEBUG=False
DATABASE_URL=your_database_url
EMAIL_HOST_USER=your_email_user
EMAIL_HOST_PASSWORD=your_email_password