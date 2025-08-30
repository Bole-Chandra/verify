from django.db import models
import uuid
from django.utils import timezone
import os
from datetime import date
import random
import string


class Certificate(models.Model):
    """Model to store certificate information"""

    # Unique certificate ID
    certificate_id = models.CharField(
        max_length=18,
        unique=True,
        editable=False,
        help_text="Unique identifier for the certificate"
    )

    # Student Information
    full_name = models.CharField(
        max_length=200,
        help_text="Full name of the student"
    )

    roll_number = models.CharField(
        max_length=50,
        help_text="Student roll number"
    )

    college_name = models.CharField(
        max_length=300,
        help_text="Name of the college/institution"
    )

    affiliated_name = models.CharField(
        max_length=300,
        help_text="Name of the Affiliated University"
    )

    course = models.CharField(
        max_length=200,
        help_text="Course name"
    )

    start_date = models.DateField(default=date.today)
    end_date = models.DateField(default=date.today)

    email = models.EmailField(
        help_text="Student email address"
    )

    # Certificate Files
    certificate_image = models.ImageField(
        upload_to='certificates/',
        blank=True,
        null=True,
        help_text="Generated certificate image"
    )

    certificate_pdf = models.FileField(
        upload_to='certificates/pdf/',
        blank=True,
        null=True,
        help_text="Generated certificate PDF (optional)"
    )

    # QR Code
    qr_code_image = models.ImageField(
        upload_to='qr_codes/',
        blank=True,
        null=True,
        help_text="QR code image for verification"
    )

    # Verification URL
    verification_url = models.URLField(
        blank=True,
        help_text="URL for certificate verification"
    )

    # Status and Timestamps
    is_verified = models.BooleanField(
        default=True,
        help_text="Whether the certificate is verified"
    )

    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="Certificate creation timestamp"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Last update timestamp"
    )

    # Email and Drive Status
    email_sent = models.BooleanField(
        default=False,
        help_text="Whether email has been sent"
    )

    email_sent_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Email sent timestamp"
    )

    drive_uploaded = models.BooleanField(
        default=False,
        help_text="Whether uploaded to Google Drive"
    )

    drive_file_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Google Drive file ID"
    )

    drive_uploaded_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Drive upload timestamp"
    )

    # Additional metadata
    notes = models.TextField(
        blank=True,
        help_text="Additional notes or comments"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Certificate"
        verbose_name_plural = "Certificates"

    def __str__(self):
        return f"Certificate for {self.full_name} - {self.course}"


    from decouple import config
    def get_verification_url(self):
        """Generate verification URL for the certificate"""
        protocol = 'https'
        domain = 'verify.cscindia.org.in'
        return f"{protocol}://{domain}/verify/{self.certificate_id}/"

    def get_certificate_filename(self):
        """Generate filename for certificate image"""
        return f"certificate_{self.certificate_id}.png"

    def get_qr_filename(self):
        """Generate filename for QR code image"""
        return f"qr_{self.certificate_id}.png"

    def save(self, *args, **kwargs):
        """Override save to set verification URL"""
        if not self.certificate_id:
            new_id = generate_certificate_id()
            while Certificate.objects.filter(certificate_id=new_id).exists():
                new_id = generate_certificate_id()
            self.certificate_id = new_id
        if not self.verification_url:
            self.verification_url = self.get_verification_url()
        super().save(*args, **kwargs)
        
def generate_certificate_id():
        prefix = "CSCIndia-"
        suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
        return prefix + suffix

class CertificateTemplate(models.Model):
    """Model to store certificate template configurations"""

    name = models.CharField(
        max_length=100,
        help_text="Template name"
    )

    template_image = models.ImageField(
        upload_to='templates/',
        help_text="Template image file"
    )

    # Text positioning coordinates
    name_x = models.IntegerField(default=400, help_text="X coordinate for name")
    name_y = models.IntegerField(default=300, help_text="Y coordinate for name")

    course_x = models.IntegerField(default=400, help_text="X coordinate for course")
    course_y = models.IntegerField(default=350, help_text="Y coordinate for course")

    college_x = models.IntegerField(default=400, help_text="X coordinate for college")
    college_y = models.IntegerField(default=400, help_text="Y coordinate for college")

    roll_x = models.IntegerField(default=200, help_text="X coordinate for roll number")
    roll_y = models.IntegerField(default=500, help_text="Y coordinate for roll number")

    cert_id_x = models.IntegerField(default=100, help_text="X coordinate for certificate ID")
    cert_id_y = models.IntegerField(default=515, help_text="Y coordinate for certificate ID")

    date_x = models.IntegerField(default=100, help_text="X coordinate for date")
    date_y = models.IntegerField(default=541, help_text="Y coordinate for date")

    qr_x = models.IntegerField(default=360, help_text="X coordinate for QR code")
    qr_y = models.IntegerField(default=465, help_text="Y coordinate for QR code")

    # Font settings
    font_size = models.IntegerField(default=24, help_text="Font size for text")
    font_color = models.CharField(
        max_length=7,
        default="#000000",
        help_text="Font color in hex format"
    )

    is_active = models.BooleanField(
        default=True,
        help_text="Whether this template is active"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Certificate Template"
        verbose_name_plural = "Certificate Templates"

    def __str__(self):
        return f"Template: {self.name}"


from django.db import models
from datetime import date
class Certificate_student(models.Model):
    full_name = models.CharField(max_length=100)
    course = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=50)
    college_name = models.CharField(max_length=200)
    affiliated_name = models.CharField(max_length=200)
    start_date = models.DateField(default=date.today)
    end_date = models.DateField(default=date.today)
    email = models.EmailField()
    contact = models.CharField(max_length=20)
    gender = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name


class CertificateExcelUpload(models.Model):
    excel_file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

