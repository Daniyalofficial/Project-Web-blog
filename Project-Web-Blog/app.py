"""
GZTECHIZ - Professional Blog Platform
FINAL WORKING VERSION - Auto Database Reset
"""

import os
import secrets
import json
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from slugify import slugify

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv(encoding='utf-8')
except:
    pass

# Initialize Flask app
app = Flask(__name__)

# Security Configuration
app.secret_key = os.getenv('SECRET_KEY', secrets.token_hex(32))
FIRST_LOGIN_KEY = 'has_seen_welcome'

# Database Configuration
database_url = os.getenv('DATABASE_URL', 'sqlite:///blog.db')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# File Upload Configuration
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

# Create upload folder if not exists
Path(app.config['UPLOAD_FOLDER']).mkdir(parents=True, exist_ok=True)

# Initialize database
db = SQLAlchemy(app)

# Admin credentials
ADMIN_EMAIL = 'gztechiz@admin.com'
ADMIN_PASSWORD = 'gulzaib077'
# ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'admin@example.com')
# ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'admin123')

# ==================== SIMPLE MODELS ====================
# Simple models without new columns for now
class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    slug = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Category {self.name}>'

class Blog(db.Model):
    __tablename__ = 'blogs'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    subtitle = db.Column(db.String(250))
    author = db.Column(db.String(50), default='Admin')
    readtime = db.Column(db.String(20), default='5 min read')
    content = db.Column(db.Text, nullable=False)
    excerpt = db.Column(db.String(300))
    slug = db.Column(db.String(150), unique=True, nullable=False)
    image = db.Column(db.String(100))
    views = db.Column(db.Integer, default=0)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    
    # TEMPORARILY COMMENTED - Add these later
    # meta_title = db.Column(db.String(200))
    # meta_description = db.Column(db.String(300))
    # meta_keywords = db.Column(db.String(200))
    # og_image = db.Column(db.String(100))
    
    category = db.relationship('Category', backref='blogs')
    
    def __repr__(self):
        return f'<Blog {self.title}>'

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    text = db.Column(db.Text, nullable=False)
    is_approved = db.Column(db.Boolean, default=True)
    post_id = db.Column(db.Integer, db.ForeignKey('blogs.id'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), nullable=True)  # ✅ This should exist
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    post = db.relationship('Blog', backref='comments')
    
    # Add this relationship for nested comments:
    children = db.relationship('Comment',
                              backref=db.backref('parent', remote_side=[id]),
                              lazy='dynamic')  # ✅ Add this line
    
    def __repr__(self):
        return f'<Comment by {self.name}>'
# ==================== HELPER FUNCTIONS ====================
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file):
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        unique_filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        return unique_filename
    return None

def generate_excerpt(content, length=150):
    # Remove HTML tags
    import re
    text = re.sub(r'<[^>]+>', '', content)
    if len(text) > length:
        return text[:length] + '...'
    return text

# ==================== CONTEXT PROCESSORS ====================
@app.context_processor
def inject_global_data():
    try:
        categories = Category.query.order_by(Category.name).all()
        recent_posts = Blog.query.filter_by(is_published=True)\
            .order_by(Blog.created_at.desc())\
            .limit(5)\
            .all()
    except Exception as e:
        print(f"Context processor error: {e}")
        categories = []
        recent_posts = []
    
    return dict(
        categories=categories,
        recent_posts=recent_posts,
        current_year=datetime.utcnow().year,
        now=datetime.utcnow()
    )

# ==================== ERROR HANDLERS ====================
@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('errors/500.html'), 500

# ==================== PUBLIC ROUTES ====================
@app.route('/')
def home():
    """Homepage with featured posts"""
    try:
        featured_posts = Blog.query.filter_by(is_published=True)\
            .order_by(Blog.created_at.desc())\
            .limit(6)\
            .all()
        total_posts = Blog.query.count()
    except Exception as e:
        print(f"Home page error: {e}")
        featured_posts = []
        total_posts = 0
    
    # Calculate stats for homepage
    stats = {
        'total_posts': total_posts or 0,
        'total_categories': Category.query.count() if Category.query.count() else 0,
        'total_comments': Comment.query.count() if Comment.query.count() else 0,
        'total_views': sum(post.views for post in featured_posts) if featured_posts else 0
    }
    
    return render_template('home.html', posts=featured_posts, stats=stats)

@app.route('/blog')
def blog_list():
    """Paginated blog listing"""
    page = request.args.get('page', 1, type=int)
    per_page = 9
    
    try:
        posts_query = Blog.query.filter_by(is_published=True)\
            .order_by(Blog.created_at.desc())
        
        # Simple pagination for now
        posts = posts_query.limit(per_page).offset((page-1)*per_page).all()
        total_posts = posts_query.count()
        total_pages = (total_posts + per_page - 1) // per_page
        
        pagination = type('obj', (object,), {
            'items': posts,
            'page': page,
            'pages': total_pages,
            'has_prev': page > 1,
            'has_next': page < total_pages,
            'prev_num': page - 1,
            'next_num': page + 1
        })
        
    except Exception as e:
        print(f"Blog list error: {e}")
        posts = []
        pagination = None
    
    return render_template('blog.html', 
                         posts=posts, 
                         pagination=pagination,
                         page=page)

@app.route('/category/<slug>')
def category_view(slug):
    """Posts by category"""
    try:
        category = Category.query.filter_by(slug=slug).first()
        if not category:
            flash('Category not found', 'error')
            return redirect(url_for('blog_list'))
            
        posts = Blog.query.filter_by(category_id=category.id, is_published=True)\
            .order_by(Blog.created_at.desc())\
            .all()
    except Exception as e:
        print(f"Category view error: {e}")
        flash('Error loading category', 'error')
        return redirect(url_for('blog_list'))
    
    return render_template('category.html', category=category, posts=posts)

@app.route('/post/<slug>', methods=['GET', 'POST'])
def post(slug):
    """Single blog post with comments"""
    try:
        post = Blog.query.filter_by(slug=slug, is_published=True).first()
        if not post:
            flash('Post not found', 'error')
            return redirect(url_for('blog_list'))
        
        # Increment view count
        post.views += 1
        db.session.commit()
        
        # Get related posts
        related_posts = Blog.query.filter(
            Blog.id != post.id,
            Blog.is_published == True
        ).order_by(Blog.created_at.desc()).limit(3).all()
        
        # Get previous and next posts
        prev_post = Blog.query.filter(
            Blog.id < post.id,
            Blog.is_published == True
        ).order_by(Blog.id.desc()).first()
        
        next_post = Blog.query.filter(
            Blog.id > post.id,
            Blog.is_published == True
        ).order_by(Blog.id.asc()).first()
        
    except Exception as e:
        print(f"Post view error: {e}")
        flash('Post not found', 'error')
        return redirect(url_for('blog_list'))
    
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        text = request.form.get('text', '').strip()
        parent_id = request.form.get('parent_id')
        
        if not all([name, email, text]):
            flash('All fields are required', 'danger')
            return redirect(url_for('post', slug=slug))
        
        comment = Comment(
            name=name,
            email=email,
            text=text,
            post_id=post.id,
            parent_id=int(parent_id) if parent_id and parent_id.isdigit() else None
        )
        
        try:
            db.session.add(comment)
            db.session.commit()
            flash('Comment submitted successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            print(f"Comment error: {e}")
            flash('Error submitting comment', 'danger')
        
        return redirect(url_for('post', slug=slug))
    
    try:
        comments = Comment.query.filter_by(post_id=post.id, is_approved=True, parent_id=None)\
            .order_by(Comment.created_at.desc())\
            .all()
    except:
        comments = []
    
    return render_template('blog_single.html', 
                         post=post, 
                         comments=comments,
                         related_posts=related_posts,
                         prev_post=prev_post,
                         next_post=next_post)

@app.route('/search')
def search():
    """Search posts"""
    query = request.args.get('q', '').strip()
    
    if not query or len(query) < 2:
        flash('Please enter at least 2 characters to search', 'warning')
        return redirect(url_for('blog_list'))
    
    try:
        # Search in title, content, and subtitle
        posts = Blog.query.filter(
            Blog.is_published == True,
            Blog.title.ilike(f'%{query}%') | 
            Blog.content.ilike(f'%{query}%') |
            Blog.subtitle.ilike(f'%{query}%')
        ).order_by(Blog.created_at.desc()).all()
        
        # Calculate results count
        results_count = len(posts)
        
    except Exception as e:
        print(f"Search error: {e}")
        posts = []
        results_count = 0
    
    return render_template('search.html', 
                         query=query, 
                         posts=posts,
                         results_count=results_count)
@app.route('/about')
def about():
    """About page"""
    try:
        stats = {
            'total_posts': Blog.query.count(),
            'total_categories': Category.query.count(),
            'total_comments': Comment.query.count(),
            'total_views': 50000
        }
    except:
        stats = {
            'total_posts': 100,
            'total_categories': 10,
            'total_comments': 500,
            'total_views': 50000
        }
    
    return render_template('about.html', stats=stats)

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact page"""
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()
        
        if name and email and message:
            flash('Thank you for your message! We will get back to you soon.', 'success')
            return redirect(url_for('contact'))
        else:
            flash('Please fill in all fields', 'danger')
    
    return render_template('contact.html')

# ==================== ADMIN ROUTES ====================
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login"""
    if session.get('admin'):
        # Check if already seen welcome
        if request.cookies.get('has_seen_welcome'):
            return redirect(url_for('admin_panel'))
        else:
            return redirect(url_for('welcome_gift'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        
        if not email or not password:
            flash('Please fill in both email and password', 'danger')
            return render_template('admin/login.html')
        
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session['admin'] = True
            flash('Login successful!', 'success')
            
            # Check if first time
            if request.cookies.get('has_seen_welcome'):
                return redirect(url_for('admin_panel'))
            else:
                return redirect(url_for('welcome_gift'))
        else:
            flash('Invalid email or password', 'danger')
    
    return render_template('admin/login.html')
@app.route('/welcome')
def welcome_gift():
    """Show welcome gift page only once"""
    # Check if user has seen welcome before
    if request.cookies.get('has_seen_welcome'):
        return redirect(url_for('admin_panel' if session.get('admin') else 'home'))
    
    # Check if admin is logged in (only show to admin)
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    return render_template('welcome_popup.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin', None)
    flash('Logged out successfully', 'info')
    return redirect(url_for('home'))

@app.route('/admin/panel')
def admin_panel():
    """Admin dashboard"""
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    # Check if this is first login (no cookie)
    if not request.cookies.get('has_seen_welcome'):
        return redirect(url_for('welcome_gift'))
    
    # Rest of your existing code...
    try:
        posts = Blog.query.order_by(Blog.created_at.desc()).all()
        stats = {
            'total_posts': Blog.query.count(),
            'total_categories': Category.query.count(),
            'total_comments': Comment.query.count(),
            'total_views': sum(post.views for post in posts) if posts else 0
        }
    except Exception as e:
        print(f"Admin panel error: {e}")
        posts = []
        stats = {
            'total_posts': 0,
            'total_categories': 0,
            'total_comments': 0,
            'total_views': 0
        }
    
    return render_template('admin/admin.html', posts=posts, stats=stats)

@app.route('/admin/add', methods=['GET', 'POST'])
def add_blog():
    """Add new blog post"""
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        # Get form data
        title = request.form.get('title', '').strip()
        subtitle = request.form.get('subtitle', '').strip()
        author = request.form.get('author', 'Admin').strip()
        readtime = request.form.get('readtime', '5 min read').strip()
        content = request.form.get('content', '').strip()
        category_name = request.form.get('category', '').strip()
        
        # Validation
        if not title:
            flash('Title is required', 'danger')
            return redirect(url_for('add_blog'))
        
        if not content:
            flash('Content is required', 'danger')
            return redirect(url_for('add_blog'))
        
        # Generate slug
        slug = request.form.get('slug', '').strip()
        if not slug:
            slug = slugify(title)
        
        # Handle duplicate slug
        existing = Blog.query.filter_by(slug=slug).first()
        if existing:
            slug = f"{slug}-{datetime.utcnow().strftime('%Y%m%d')}"
        
        # Handle category
        category_id = None
        if category_name:
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                category = Category(
                    name=category_name,
                    slug=slugify(category_name)
                )
                try:
                    db.session.add(category)
                    db.session.flush()
                except:
                    db.session.rollback()
                    flash('Error creating category', 'danger')
                    return redirect(url_for('add_blog'))
            category_id = category.id
        
        # Handle image upload
        image_file = request.files.get('image')
        image_filename = None
        if image_file and image_file.filename:
            image_filename = save_uploaded_file(image_file)
        
        # Generate excerpt
        excerpt = generate_excerpt(content)
        
        # Create blog post
        blog = Blog(
            title=title,
            subtitle=subtitle,
            author=author,
            readtime=readtime,
            content=content,
            excerpt=excerpt,
            slug=slug,
            image=image_filename,
            category_id=category_id
        )
        
        try:
            db.session.add(blog)
            db.session.commit()
            flash('Blog post published successfully!', 'success')
        except Exception as e:
            db.session.rollback()
            print(f"Add blog error: {e}")
            flash('Error publishing post', 'danger')
        
        return redirect(url_for('admin_panel'))
    
    return render_template('admin/add.html')

@app.route('/admin/edit/<int:id>', methods=['GET', 'POST'])
def edit_blog(id):
    """Edit blog post"""
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    try:
        blog = Blog.query.get(id)
        if not blog:
            flash('Blog post not found', 'danger')
            return redirect(url_for('admin_panel'))
    except:
        flash('Blog post not found', 'danger')
        return redirect(url_for('admin_panel'))
    
    if request.method == 'POST':
        blog.title = request.form.get('title', '').strip()
        blog.subtitle = request.form.get('subtitle', '').strip()
        blog.author = request.form.get('author', 'Admin').strip()
        blog.readtime = request.form.get('readtime', '5 min read').strip()
        blog.content = request.form.get('content', '').strip()
        
        # Update slug if provided
        new_slug = request.form.get('slug', '').strip()
        if new_slug and new_slug != blog.slug:
            blog.slug = slugify(new_slug)
        
        # Update category
        category_name = request.form.get('category', '').strip()
        if category_name:
            category = Category.query.filter_by(name=category_name).first()
            if not category:
                category = Category(name=category_name, slug=slugify(category_name))
                db.session.add(category)
                db.session.flush()
            blog.category_id = category.id
        else:
            blog.category_id = None
        
        # Update image
        image_file = request.files.get('image')
        if image_file and image_file.filename:
            # Delete old image if exists
            if blog.image:
                old_path = os.path.join(app.config['UPLOAD_FOLDER'], blog.image)
                if os.path.exists(old_path):
                    os.remove(old_path)
            blog.image = save_uploaded_file(image_file)
        
        blog.excerpt = generate_excerpt(blog.content)
        blog.updated_at = datetime.utcnow()
        
        try:
            db.session.commit()
            flash('Blog post updated successfully!', 'success')
        except:
            db.session.rollback()
            flash('Error updating post', 'danger')
        
        return redirect(url_for('admin_panel'))
    
    return render_template('admin/edit.html', post=blog)

@app.route('/admin/delete/<int:id>')
def delete_blog(id):
    """Delete blog post"""
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    try:
        blog = Blog.query.get(id)
        if not blog:
            flash('Blog post not found', 'danger')
            return redirect(url_for('admin_panel'))
        
        # Delete associated images
        if blog.image:
            image_path = os.path.join(app.config['UPLOAD_FOLDER'], blog.image)
            if os.path.exists(image_path):
                os.remove(image_path)
        
        db.session.delete(blog)
        db.session.commit()
        flash('Blog post deleted successfully!', 'success')
    except Exception as e:
        db.session.rollback()
        print(f"Delete error: {e}")
        flash('Error deleting post', 'danger')
    
    return redirect(url_for('admin_panel'))

@app.route('/admin/change-password', methods=['GET', 'POST'])
def change_password():
    """Change admin password"""
    if not session.get('admin'):
        return redirect(url_for('admin_login'))
    
    if request.method == 'POST':
        current = request.form.get('current_password', '')
        new = request.form.get('new_password', '')
        confirm = request.form.get('confirm_password', '')
        
        if current == ADMIN_PASSWORD:
            if new == confirm:
                if len(new) >= 8:
                    flash('Password changed successfully! (Note: Update .env file for permanent change)', 'success')
                    return redirect(url_for('admin_panel'))
                else:
                    flash('Password must be at least 8 characters', 'danger')
            else:
                flash('New passwords do not match', 'danger')
        else:
            flash('Current password is incorrect', 'danger')
    
    return render_template('admin/change_password.html')

# ==================== API ROUTES ====================
@app.route('/api/search')
def api_search():
    """API for live search"""
    query = request.args.get('q', '').strip()
    if not query or len(query) < 2:
        return jsonify([])
    
    try:
        posts = Blog.query.filter(
            Blog.is_published == True,
            Blog.title.ilike(f'%{query}%')
        ).limit(8).all()
    except:
        posts = []
    
    results = []
    for post in posts:
        results.append({
            'title': post.title,
            'slug': post.slug,
            'excerpt': post.excerpt or generate_excerpt(post.content, 100)
        })
    
    return jsonify(results)

# ==================== STATIC FILES ====================
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ==================== INITIALIZATION ====================
def init_db():
    with app.app_context():
        try:
            # Drop all tables and recreate
            db.drop_all()
            db.create_all()
            
            # Create default category
            default = Category(name='Uncategorized', slug='uncategorized')
            db.session.add(default)
            
            # Create sample blog posts
            sample_posts = [
                Blog(
                    title='Welcome to Gztechiz Blog',
                    subtitle='A modern blog platform for tech enthusiasts',
                    author='Admin',
                    readtime='5 min read',
                    content='<p>This is your first blog post. Edit or delete it to get started!</p>',
                    excerpt='Welcome to our new blog platform...',
                    slug='welcome-to-gztechiz',
                    is_published=True
                ),
                Blog(
                    title='Getting Started with Flask',
                    subtitle='Learn how to build web applications with Python',
                    author='Admin',
                    readtime='10 min read',
                    content='<p>Flask is a lightweight WSGI web application framework...</p>',
                    excerpt='Introduction to Flask web framework...',
                    slug='getting-started-with-flask',
                    is_published=True
                )
            ]
            
            for post in sample_posts:
                db.session.add(post)
            
            db.session.commit()
            print("✓ Database initialized successfully!")
            print("✓ Created default category: Uncategorized")
            print("✓ Created 2 sample blog posts")
            
        except Exception as e:
            print(f"✗ Database initialization error: {str(e)}")
            import traceback
            traceback.print_exc()

# Initialize database
init_db()

# ==================== MAIN ====================
if __name__ == '__main__':
    print("=" * 50)
    print("🚀 GZTECHIZ BLOG PLATFORM")
    print("=" * 50)
    print(f"📧 Admin Email: {ADMIN_EMAIL}")
    print("🔑 Admin Password: admin123")
    print(f"🗄️  Database: {database_url}")
    print(f"📁 Upload Folder: {app.config['UPLOAD_FOLDER']}")
    print("=" * 50)
    print("🌐 Server: http://localhost:5000")
    print("⚙️  Admin: http://localhost:5000/admin/login")
    print("=" * 50)
    print("✅ Ready! Press Ctrl+C to stop")
    print("=" * 50)
    
    app.run(debug=True, host='0.0.0.0', port=5000)