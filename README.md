# WonderFloyd

**Discover:** [wonderfloyd.com](https://wonderfloyd.com)

**Current version:** `1.1.2`

<img src="static/assets/img/wf-preview.png" width="850">

WonderFloyd is a digital space designed for those who never stop asking questions about science, life, technology, and the wonders that connect them all. It is a platform designed to share timeless, engaging, and engrossing ideas with the world.

WonderFloyd’s vision rises from the intersection of scientific curiosity, philosophical depth, and artistic expression.

The goal is simple: to produce content that is reliable, informative and enjoyable. Every piece aims to be clear, accurate and inspiring.

Long form writing is paired with short visual content, offering a smooth and modern reading experience across devices.

## Features
- Full blog platform powered by Flask
- Dynamic post system with slugs
- Many-to-many category system
- Dynamic filtering with fetch-based partial updates
- CKEditor 5 integration
- Inline image upload with automatic WebP conversion
- Hero and thumbnail image processing
- Beautiful dark and light theme
- SMTP powered contact form
- Admin panel for creating and editing posts
- SEO friendly structure
- Smooth animations and reveal effects
- Optimized rendering with staggered animations
- Fully responsive layout
- Custom design and brand identity
- Fully user-friendly

## Tech Stack
- Python
- Flask
- SQLAlchemy
- SQLite (production ready for PostgreSQL)
- Bootstrap 5
- CKEditor 5
- Pillow (image processing)
- Vanilla JavaScript
- HTML / Jinja
- CSS

## Project Structure
```
WonderFloyd/
│
├── static/
│   ├── assets/
│   │   ├── favicons/
│   │   └── img/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── scripts.js
│   └── uploads/
│
├── templates/
│   ├── partials/
│   │   └── post-list.html
│   ├── about.html
│   ├── contact.html
│   ├── footer.html
│   ├── header.html
│   ├── index.html
│   ├── make-post.html
│   ├── post.html
│   ├── privacy.html
│   ├── terms.html
│   └── secret-login.html
│
├── app.py
├── forms.py
├── LICENSE
├── README.md
├── requirements.txt
├── version.py
├── wsgi.py
└── .env
```

## Installation
```
git clone <repo-url>
cd wonderfloyd
pip install -r requirements.txt
python app.py
```

## Deployment
WonderFloyd is deployed using:

- Gunicorn as the WSGI application server
- Nginx as a reverse proxy
- Let’s Encrypt SSL certificates for HTTPS
- Cloudflare for DNS, security and global asset delivery
- A lightweight VPS environment running a Linux-based OS

The project uses:

- A dedicated virtual environment
- Environment variables for secrets and configuration
- A system service to keep the application running continuously 

This setup works reliably on providers like Vultr, DigitalOcean, Linode, Hetzner and other similar VPS platforms.

## Notes
This documentation explains how the project works for development and learning purposes.
The source code, design, visual identity and written content are fully owned by the author and cannot be reused without permission.

## License
All original work within this repository is protected under All Rights Reserved.
Third party dependencies such as Bootstrap and Clean Blog remain under their MIT License.
See the LICENSE file for full details.
