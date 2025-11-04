from datetime import date, datetime
from flask import Flask, render_template, redirect, url_for, abort, request, flash, jsonify
from flask_bootstrap import Bootstrap5
from flask_ckeditor import CKEditor
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship, DeclarativeBase, Mapped, mapped_column, joinedload
from sqlalchemy import Integer, String, Text, func, Boolean
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from functools import wraps
from dotenv import load_dotenv
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import smtplib
from email.message import EmailMessage
from PIL import Image
from io import BytesIO
import os
import re
import uuid
import base64

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('FLASK_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DB_URI", "sqlite:///posts.db")
ckeditor = CKEditor(app)
Bootstrap5(app)

# Image Upload Config
app.config['MAX_CONTENT_LENGTH'] = 12 * 1024 * 1024  # 12 MB limit
UPLOADS_DIR = os.path.join(app.root_path, 'static', 'uploads')
os.makedirs(UPLOADS_DIR, exist_ok=True)

# Configure Login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

# Database setup
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Many-to-many table
post_categories = db.Table(
    "post_categories",
    db.Column("post_id", db.Integer, db.ForeignKey("blog_posts.id")),
    db.Column("category_id", db.Integer, db.ForeignKey("categories.id"))
)

# Category table
class Category(db.Model):
    __tablename__ = "categories"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    posts = relationship("BlogPost", secondary=post_categories, back_populates="categories")

# BlogPost table
class BlogPost(db.Model):
    __tablename__ = "blog_posts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    author_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    subtitle: Mapped[str] = mapped_column(String(250), nullable=False)
    date: Mapped[str] = mapped_column(String(250), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    img_url: Mapped[str] = mapped_column(String(250), nullable=False)
    slug: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    categories = relationship("Category", secondary=post_categories, back_populates="posts")

    sources = relationship(
        "PostSource",
        back_populates="post",
        cascade="all, delete-orphan",
        order_by="PostSource.order"
    )

class PostSource(db.Model):
    __tablename__ = "post_sources"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    post_id: Mapped[int] = mapped_column(Integer, db.ForeignKey("blog_posts.id"), nullable=False)

    # simple & flexible
    order: Mapped[int] = mapped_column(Integer, default=0)  # display order
    label: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(String(1000), nullable=True)    # optional link

    post = relationship("BlogPost", back_populates="sources")


# Admin User table
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    password: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    posts = relationship("BlogPost", back_populates="author")

with app.app_context():
    db.create_all()

ALLOWED_EXTS = {'jpg', 'jpeg', 'png', 'webp'}

def _allowed(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTS

def _to_webp_bytes(pil_img: Image.Image, quality=82) -> bytes:
    out = BytesIO()
    pil_img.save(out, format='WEBP', quality=quality, method=6)
    out.seek(0)
    return out.read()

def _resize_cover(pil_img: Image.Image, target_w=1920, target_h=1080) -> Image.Image:
    img = pil_img.convert('RGB')
    ratio = max(target_w / img.width, target_h / img.height)
    new_size = (int(img.width * ratio), int(img.height * ratio))
    img = img.resize(new_size, Image.LANCZOS)
    left = (img.width - target_w) // 2
    top = (img.height - target_h) // 2
    right = left + target_w
    bottom = top + target_h
    return img.crop((left, top, right, bottom))

def _resize_thumb(pil_img: Image.Image, max_w=600, max_h=400) -> Image.Image:
    img = pil_img.convert('RGB')
    img.thumbnail((max_w, max_h), Image.LANCZOS)
    return img

def save_post_images(file_storage, slug: str) -> dict:
    """
    It creates hero.webp and thumb.webp from the giving file.
    Return: {'hero': '/static/uploads/<slug>/hero.webp', 'thumb': '/static/uploads/<slug>/thumb.webp'}
    """
    if not file_storage or file_storage.filename == '':
        return {}

    if not _allowed(file_storage.filename):
        raise ValueError("Unsupported file type")

    base = secure_filename(slug or uuid.uuid4().hex)
    folder = os.path.join(UPLOADS_DIR, base)
    os.makedirs(folder, exist_ok=True)

    file_storage.stream.seek(0)
    img = Image.open(file_storage.stream)
    img.verify()
    file_storage.stream.seek(0)
    img = Image.open(file_storage.stream).convert('RGB')

    hero = _resize_cover(img, 1920, 1080)
    thumb = _resize_thumb(img, 600, 400)

    hero_bytes = _to_webp_bytes(hero, quality=82)
    thumb_bytes = _to_webp_bytes(thumb, quality=80)

    hero_path = os.path.join(folder, "hero.webp")
    thumb_path = os.path.join(folder, "thumb.webp")

    with open(hero_path, "wb") as f:
        f.write(hero_bytes)
    with open(thumb_path, "wb") as f:
        f.write(thumb_bytes)

    public_folder = f"/static/uploads/{base}"
    return {
        "hero": f"{public_folder}/hero.webp",
        "thumb": f"{public_folder}/thumb.webp",
    }

def _resize_inline(img: Image.Image, max_w=1600, max_h=1600) -> Image.Image:
    """Keep aspect ratio, fit into max box, no crop."""
    im = img.convert("RGB")
    im.thumbnail((max_w, max_h), Image.LANCZOS)
    return im

def save_inline_image(file_storage: FileStorage) -> str:
    """Save an inline image as webp under /static/uploads/inline/ and return public URL."""
    if not file_storage or file_storage.filename == '':
        raise ValueError("No file provided")
    if not _allowed(file_storage.filename):
        raise ValueError("Unsupported file type")

    # 1) Target folder: /static/uploads/inline
    folder = os.path.join(UPLOADS_DIR, "inline")
    os.makedirs(folder, exist_ok=True)

    # 2) Read & validate
    file_storage.stream.seek(0)
    img = Image.open(file_storage.stream)
    img.verify()
    file_storage.stream.seek(0)
    img = Image.open(file_storage.stream).convert("RGB")

    # 3) Resize to fit (max 1600px edge) + save webp
    out_img = _resize_inline(img, 1600, 1600)
    fname = f"{uuid.uuid4().hex}.webp"
    fpath = os.path.join(folder, fname)
    with open(fpath, "wb") as f:
        f.write(_to_webp_bytes(out_img, quality=82))

    # 4) Return public URL
    return f"/static/uploads/inline/{fname}"

def replace_base64_images_with_files(html: str) -> str:
    """Convert <img src="data:image/...;base64, ..."> to files under /static/uploads/inline/ and replace src."""
    if not html:
        return html

    # png|jpg|jpeg|webp|gif  (+ whitespace tolerant base64)
    pattern = re.compile(
        r'src=["\']data:image/(png|jpe?g|webp|gif);base64,([A-Za-z0-9+/=\s]+)["\']',
        re.IGNORECASE | re.DOTALL
    )

    def _save_and_replace(m: re.Match) -> str:
        b64 = m.group(2).replace('\n', '').replace('\r', '').replace(' ', '')
        try:
            raw = base64.b64decode(b64)
        except Exception:
            return m.group(0)

        try:
            img = Image.open(BytesIO(raw))
            if img.mode != "RGB":
                img = img.convert("RGB")
        except Exception:
            return m.group(0)

        out = _resize_inline(img, 1600, 1600)
        folder = os.path.join(UPLOADS_DIR, "inline")
        os.makedirs(folder, exist_ok=True)
        fname = f"{uuid.uuid4().hex}.webp"
        with open(os.path.join(folder, fname), "wb") as f:
            f.write(_to_webp_bytes(out, quality=82))

        url = f"/static/uploads/inline/{fname}"
        return f'src="{url}"'

    return pattern.sub(_save_and_replace, html)

def send_contact_mail(name: str, email: str, subject: str, message: str):
    """Send email via SMTP (TLS). Reply-To will be the sender's email."""
    smtp_host = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    smtp_port = int(os.environ.get("SMTP_PORT", "587"))
    smtp_user = os.environ.get("SMTP_USER")
    smtp_pass = os.environ.get("SMTP_PASSWORD")
    admin_to = os.environ.get("ADMIN_EMAIL", smtp_user)

    if not (smtp_user and smtp_pass and admin_to):
        raise RuntimeError("SMTP configuration is missing. Check your .env variables.")

    msg = EmailMessage()
    title = subject.strip() if subject else f"New message from {name}"
    msg["Subject"] = f"[WonderFloyd • Contact] {title}"
    msg["From"] = smtp_user
    msg["To"] = admin_to
    msg["Reply-To"] = email

    body = (
        f"New contact message from WonderFloyd:\n\n"
        f"Name   : {name}\n"
        f"Email  : {email}\n"
        f"Subject: {subject or '-'}\n"
        f"Date   : {datetime.now().isoformat(timespec='seconds')}\n\n"
        f"Message:\n{message}\n"
    )
    msg.set_content(body)

    with smtplib.SMTP(smtp_host, smtp_port, timeout=20) as server:
        server.ehlo()
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)

# Admin-only decorator
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function

def generate_slug(title):
    slug = re.sub(r'[\W_]+', '-', title.lower())
    return slug.strip('-')

# ROUTES
@app.route('/')
def get_all_posts():
    LIMIT = 10
    base_query = (
        db.session.query(BlogPost)
        .options(
            joinedload(BlogPost.author),
            joinedload(BlogPost.categories)
        )
    )
    total_count = base_query.count()
    posts = (
        base_query
        .order_by(BlogPost.id.desc())
        .limit(LIMIT)
        .all()
    )
    initial_has_more = LIMIT < total_count
    return render_template(
        "index.html",
        posts=posts,
        current_user=current_user,
        initial_has_more=initial_has_more
    )

@app.route("/<string:slug>")
def show_post(slug):
    requested_post = (
        db.session.query(BlogPost)
        .options(
            joinedload(BlogPost.author),
            joinedload(BlogPost.categories),
            joinedload(BlogPost.sources)   # <-- eklendi
        )
        .filter(BlogPost.slug == slug)
        .first()
    )
    if not requested_post:
        abort(404)

    return render_template("post.html", post=requested_post, current_user=current_user)

from forms import CreatePostForm
from forms import ContactForm


@app.route("/filter-posts/<int:category_id>")
def filter_posts(category_id):
    try:
        offset = int(request.args.get("offset", 0))
        limit = int(request.args.get("limit", 10))
    except ValueError:
        offset, limit = 0, 10

    base_query = (
        db.session.query(BlogPost)
        .options(
            joinedload(BlogPost.author),
            joinedload(BlogPost.categories)
        )
    )

    if category_id != 0:
        base_query = (
            base_query
            .join(BlogPost.categories)
            .filter(Category.id == category_id)
        )

    total_count = base_query.count()
    posts = (
        base_query
        .order_by(BlogPost.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    has_more = (offset + limit) < total_count
    html = render_template("partials/post-list.html", posts=posts)
    return {"html": html, "has_more": has_more}

@app.route("/ultra-secret-login", methods=["GET", "POST"])
def secret_login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")
        user = db.session.execute(db.select(User).where(User.email == email)).scalar()

        if user and check_password_hash(user.password, password):
            login_user(user)
            flash("Admin login successful ✨")
            return redirect(url_for("get_all_posts"))
        else:
            flash("Invalid login information 😢")
            return redirect(url_for("secret_login"))

    return render_template("secret-login.html")

@app.route("/new-post", methods=["GET", "POST"])
@admin_only
def add_new_post():
    form = CreatePostForm()
    form.categories.choices = [(cat.id, cat.name) for cat in db.session.query(Category).all()]

    if form.validate_on_submit():
        # Fetch selected categories
        selected_categories = (
            db.session.query(Category)
            .filter(Category.id.in_(form.categories.data))
            .all()
        )

        # Generate slug from title
        post_slug = generate_slug(form.title.data)

        # Cover image (hero/thumb) handling
        img_url_value = form.img_url.data or ""
        file_storage: FileStorage = request.files.get('cover_image')
        if file_storage and file_storage.filename:
            try:
                saved = save_post_images(file_storage, post_slug)
                if saved.get("hero"):
                    img_url_value = saved["hero"]
            except Exception as e:
                flash(f"Image upload failed: {e}")
                return redirect(url_for("add_new_post"))

        # Convert any base64 inline images to files
        cleaned_body = replace_base64_images_with_files(form.body.data)

        # Create the post
        new_post = BlogPost(
            title=form.title.data,
            subtitle=form.subtitle.data,
            body=cleaned_body,
            img_url=img_url_value if img_url_value else "/static/assets/img/placeholder-hero.jpg",
            author=current_user,
            date=date.today().strftime("%b %d, %Y"),
            slug=post_slug,
            categories=selected_categories
        )

        # Build sources from FieldList (label required to persist; URL optional)
        order_idx = 0
        for subform in form.sources.entries:
            lbl = (subform.form.label.data or "").strip()
            url = (subform.form.url.data or "").strip()
            if not lbl:
                continue
            new_post.sources.append(PostSource(order=order_idx, label=lbl, url=(url or None)))
            order_idx += 1

        db.session.add(new_post)
        db.session.commit()
        return redirect(url_for("get_all_posts"))

    return render_template("make-post.html", form=form, current_user=current_user)


@app.route("/edit-post/<int:post_id>", methods=["GET", "POST"])
@admin_only
def edit_post(post_id):
    post = db.get_or_404(BlogPost, post_id)

    # Pre-fill base fields
    form = CreatePostForm(
        title=post.title,
        subtitle=post.subtitle,
        img_url=post.img_url,
        body=post.body,
        categories=[cat.id for cat in post.categories]
    )
    form.categories.choices = [(cat.id, cat.name) for cat in db.session.query(Category).all()]

    # On GET: prefill FieldList with existing sources (show existing + pad to min_entries)
    if request.method == "GET":
        # Clear auto-created empty entries
        form.sources.entries = []
        for s in (post.sources or []):
            form.sources.append_entry({"label": s.label or "", "url": s.url or ""})
        while len(form.sources.entries) < form.sources.min_entries:
            form.sources.append_entry()

    if form.validate_on_submit():
        # Update basic fields
        post.title = form.title.data
        post.subtitle = form.subtitle.data
        post.img_url = form.img_url.data or post.img_url

        # Convert any base64 inline images to files as well on edit
        post.body = replace_base64_images_with_files(form.body.data)

        # Update categories
        post.categories = (
            db.session.query(Category)
            .filter(Category.id.in_(form.categories.data))
            .all()
        )

        # Optional: replace hero if a new cover uploaded
        file_storage: FileStorage = request.files.get('cover_image')
        if file_storage and file_storage.filename:
            try:
                saved = save_post_images(file_storage, post.slug or generate_slug(post.title))
                if saved.get("hero"):
                    post.img_url = saved["hero"]
            except Exception as e:
                flash(f"Image upload failed: {e}")
                return redirect(url_for("edit_post", post_id=post.id))

        # Replace sources atomically (clear + rebuild)
        post.sources.clear()
        order_idx = 0
        for subform in form.sources.entries:
            lbl = (subform.form.label.data or "").strip()
            url = (subform.form.url.data or "").strip()
            if not lbl:
                continue
            post.sources.append(PostSource(order=order_idx, label=lbl, url=(url or None)))
            order_idx += 1

        db.session.commit()
        return redirect(url_for("show_post", slug=post.slug))

    return render_template("make-post.html", form=form, is_edit=True, current_user=current_user)


@app.route("/upload-image", methods=["POST"])
@admin_only
def upload_image():
    try:
        # CKEditor 5 may send under 'upload' (SimpleUpload) or 'file'
        fs = request.files.get("upload") or request.files.get("file")
        if not fs:
            return jsonify({"error": {"message": "No file part"}}), 400

        # Basic size check (uses app.config['MAX_CONTENT_LENGTH'] globally)
        url = save_inline_image(fs)
        return jsonify({"url": url}), 201

    except ValueError as ve:
        return jsonify({"error": {"message": str(ve)}}), 400
    except Exception as e:
        # Log e if you have logging
        return jsonify({"error": {"message": "Upload failed"}}), 500

@app.route("/delete/<int:post_id>")
@admin_only
def delete_post(post_id):
    post_to_delete = db.get_or_404(BlogPost, post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for('get_all_posts'))

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("get_all_posts"))

@app.route("/about")
def about():
    return render_template("about.html", current_user=current_user)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    form = ContactForm()

    if form.validate_on_submit():
        if form.website.data:
            flash("Thanks! Your message has been received.", "success")
            return redirect(url_for("contact"))

        try:
            send_contact_mail(
                name=form.name.data.strip(),
                email=form.email.data.strip(),
                subject=(form.subject.data or "").strip(),
                message=form.message.data.strip(),
            )
            flash("Message sent successfully. We’ll get back to you soon ✨", "success")
            return redirect(url_for("contact"))  # PRG pattern
        except Exception as e:
            # Optionally log e
            flash("Oops, message could not be sent. Please try again later.", "danger")

    return render_template("contact.html", form=form, current_user=current_user)

@app.context_processor
def inject_year():
    return {"current_year": datetime.now().year}

if __name__ == "__main__":
    app.run(debug=True, port=5001)
