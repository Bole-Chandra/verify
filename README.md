# Certificate Generation System

A comprehensive Django-based web application for generating, verifying, and managing digital certificates with QR code verification, email integration, and Google Drive backup functionality.

## 🌟 Features

### Core Functionality
- **Certificate Generation**: Generate professional certificates using customizable templates
- **QR Code Verification**: Each certificate includes a unique QR code for instant verification
- **Email Integration**: Automatically send certificates to recipients via email
- **Google Drive Backup**: Automatic backup of certificates to Google Drive
- **Admin Dashboard**: Comprehensive admin panel for certificate management

### Frontend Features
- **Responsive Design**: Mobile-friendly interface with Bootstrap styling
- **Interactive Forms**: User-friendly certificate generation forms with validation
- **Real-time Preview**: Certificate preview with download options
- **Verification Portal**: Public verification page accessible via QR codes

### Backend Features
- **Django Framework**: Robust backend with Django ORM
- **Image Processing**: PIL-based certificate generation with text overlay
- **UUID Generation**: Unique certificate IDs for security
- **Database Management**: SQLite database with admin interface
- **API Integration**: Google Drive API and email services

## 🚀 Quick Start

### Prerequisites
- Python 3.11 or higher
- pip (Python package installer)
- Git (for cloning the repository)

### Installation

1. **Clone or Extract the Project**
   ```bash
   # If you have the zip file, extract it
   unzip certificate_system.zip
   cd certificate_system
   
   # Or if cloning from repository
   git clone <repository-url>
   cd certificate_system
   ```

2. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Configuration**
   ```bash
   # Copy the environment template
   cp .env.example .env
   
   # Edit .env file with your configurations
   nano .env
   ```

4. **Database Setup**
   ```bash
   # Run database migrations
   python manage.py migrate
   
   # Create a superuser for admin access
   python manage.py createsuperuser
   ```

5. **Run the Development Server**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

6. **Access the Application**
   - Main Application: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin

## 📋 Configuration

### Environment Variables (.env)

Create a `.env` file in the project root with the following variables:

```env
# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration (Optional - defaults to SQLite)
DATABASE_URL=sqlite:///db.sqlite3

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Google Drive API Configuration
GOOGLE_DRIVE_CREDENTIALS_FILE=path/to/credentials.json
GOOGLE_DRIVE_FOLDER_ID=your-drive-folder-id

# Certificate Configuration
CERTIFICATE_TEMPLATE_PATH=media/templates/certificate_template.png
CERTIFICATE_FONT_PATH=fonts/arial.ttf
```

### Google Drive Setup (Optional)

1. **Create Google Cloud Project**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Google Drive API

2. **Create Service Account**
   - Go to IAM & Admin > Service Accounts
   - Create a new service account
   - Download the JSON credentials file

3. **Configure Drive Access**
   - Create a folder in Google Drive for certificates
   - Share the folder with the service account email
   - Copy the folder ID from the URL

4. **Update Environment**
   ```env
   GOOGLE_DRIVE_CREDENTIALS_FILE=path/to/service-account.json
   GOOGLE_DRIVE_FOLDER_ID=your-folder-id
   ```

### Email Setup (Optional)

For Gmail SMTP:
1. Enable 2-factor authentication on your Google account
2. Generate an App Password for the application
3. Use the App Password in EMAIL_HOST_PASSWORD

## 🎯 Usage

### Generating Certificates

1. **Access the Application**
   - Navigate to http://localhost:8000
   - Click "Generate Certificate"

2. **Fill the Form**
   - Full Name: Student's complete name
   - Course Name: Name of the completed course
   - College/Institution: Name of the issuing institution
   - Roll Number: Student's roll/ID number
   - Email Address: Recipient's email address

3. **Submit and Download**
   - Review the information
   - Check the terms and conditions
   - Click "Generate Certificate"
   - Download the certificate in PNG or PDF format

### Verifying Certificates

1. **QR Code Scanning**
   - Scan the QR code on any certificate
   - Automatically redirects to verification page

2. **Manual Verification**
   - Go to http://localhost:8000/verify/CERTIFICATE-ID/
   - Replace CERTIFICATE-ID with the actual certificate ID

3. **Verification Results**
   - ✅ Valid certificates show verification success
   - ❌ Invalid certificates show error message

### Admin Management

1. **Access Admin Panel**
   - Navigate to http://localhost:8000/admin
   - Login with superuser credentials

2. **Certificate Management**
   - View all generated certificates
   - Filter by various criteria
   - Perform bulk actions (email, drive upload, regenerate)
   - Export certificate data

3. **User Management**
   - Create additional admin users
   - Manage user permissions
   - View user activity logs

## 🏗️ Project Structure

```
certificate_system/
├── certificate_project/          # Django project settings
│   ├── __init__.py
│   ├── settings.py               # Main configuration file
│   ├── urls.py                   # URL routing
│   └── wsgi.py                   # WSGI configuration
├── certificates/                 # Main Django app
│   ├── migrations/               # Database migrations
│   ├── __init__.py
│   ├── admin.py                  # Admin interface configuration
│   ├── apps.py                   # App configuration
│   ├── forms.py                  # Django forms
│   ├── models.py                 # Database models
│   ├── urls.py                   # App URL patterns
│   ├── utils.py                  # Utility functions
│   └── views.py                  # View functions
├── media/                        # Media files
│   ├── certificates/             # Generated certificates
│   ├── qr_codes/                # QR code images
│   └── templates/               # Certificate templates
├── static/                       # Static files
│   ├── css/                     # Stylesheets
│   ├── js/                      # JavaScript files
│   └── images/                  # Static images
├── templates/                    # HTML templates
│   ├── certificates/            # App-specific templates
│   └── base.html               # Base template
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore file
├── db.sqlite3                   # SQLite database
├── manage.py                    # Django management script
├── README.md                    # This file
└── requirements.txt             # Python dependencies
```

## 🔧 API Endpoints

### Public Endpoints
- `GET /` - Homepage
- `GET /generate/` - Certificate generation form
- `POST /generate/` - Process certificate generation
- `GET /verify/<certificate_id>/` - Certificate verification
- `GET /certificate/<certificate_id>/` - Certificate details
- `GET /download/<certificate_id>/` - Download certificate PNG
- `GET /download-pdf/<certificate_id>/` - Download certificate PDF

### Admin Endpoints
- `GET /admin/` - Admin dashboard
- `GET /admin/certificates/certificate/` - Certificate management
- `POST /admin/certificates/certificate/` - Bulk actions

## 🧪 Testing

### Manual Testing

1. **Certificate Generation**
   ```bash
   # Test with sample data
   python manage.py shell
   >>> from certificates.utils import generate_certificate
   >>> generate_certificate("Test User", "Test Course", "Test College", "TEST001", "test@example.com")
   ```

2. **QR Code Verification**
   - Generate a certificate
   - Scan the QR code with a mobile device
   - Verify the verification page loads correctly

3. **Admin Interface**
   - Login to admin panel
   - Test filtering and search functionality
   - Try bulk actions

### Automated Testing

```bash
# Run Django tests
python manage.py test

# Run with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
```

## 🚀 Deployment

### Production Deployment

1. **Update Settings**
   ```python
   # In settings.py
   DEBUG = False
   ALLOWED_HOSTS = ['your-domain.com']
   ```

2. **Collect Static Files**
   ```bash
   python manage.py collectstatic
   ```

3. **Use Production Database**
   ```bash
   # For PostgreSQL
   pip install psycopg2-binary
   # Update DATABASE_URL in .env
   ```

4. **Web Server Configuration**
   - Use Gunicorn or uWSGI
   - Configure Nginx for static files
   - Set up SSL certificates

### Docker Deployment (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD ["gunicorn", "certificate_project.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## 🛠️ Customization

### Certificate Template

1. **Replace Template Image**
   - Add your template to `media/templates/`
   - Update `CERTIFICATE_TEMPLATE_PATH` in settings

2. **Adjust Text Positioning**
   - Modify coordinates in `certificates/utils.py`
   - Test with sample data

3. **Font Customization**
   - Add custom fonts to `fonts/` directory
   - Update font paths in utils.py

### Styling

1. **CSS Customization**
   - Edit `static/css/style.css`
   - Add custom Bootstrap themes

2. **Template Modification**
   - Customize HTML templates in `templates/`
   - Add new pages or modify existing ones

## 🔍 Troubleshooting

### Common Issues

1. **Certificate Generation Fails**
   ```bash
   # Check template file exists
   ls media/templates/certificate_template.png
   
   # Verify PIL installation
   python -c "from PIL import Image; print('PIL working')"
   ```

2. **QR Code Not Generating**
   ```bash
   # Check qrcode installation
   python -c "import qrcode; print('QR code working')"
   ```

3. **Email Not Sending**
   - Verify SMTP settings in .env
   - Check firewall/network restrictions
   - Test with a simple email client

4. **Google Drive Upload Fails**
   - Verify credentials file path
   - Check folder permissions
   - Ensure API is enabled

### Debug Mode

Enable debug mode for detailed error messages:
```env
DEBUG=True
```

View Django logs:
```bash
python manage.py runserver --verbosity=2
```

## 📝 License

This project is licensed under the MIT License. See the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review Django documentation

## 🔄 Version History

### v1.0.0 (Current)
- Initial release
- Certificate generation with QR codes
- Email and Google Drive integration
- Admin panel with bulk actions
- Responsive web interface

## 🙏 Acknowledgments

- Django framework for the robust backend
- Bootstrap for responsive UI components
- PIL (Pillow) for image processing
- QR Code library for verification codes
- Google Drive API for cloud storage

---

**Note**: This is a development version. For production use, ensure proper security configurations, use environment variables for sensitive data, and implement appropriate backup strategies.

