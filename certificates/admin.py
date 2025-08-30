from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Certificate, CertificateTemplate
import csv
from django.http import HttpResponse
import datetime
import zipfile
from io import BytesIO
import os
import re


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    """Admin interface for Certificate model"""

    list_display = [
        'full_name',
        'course',
        'college_name',
        'roll_number',
        'affiliated_name',
        'course',
        'start_date',
        'end_date',
        'email',
        'certificate_image',
        'certificate_id_short',
        'is_verified',
        'email_sent',
        'drive_uploaded',
        'created_at',
    ]

    list_filter = [
        'is_verified',
        'email_sent',
        'drive_uploaded',
        'created_at',
        'course',
        'college_name'
    ]

    search_fields = [
        'full_name',
        'email',
        'roll_number',
        'course',
        'college_name',
        'certificate_id'
    ]

    readonly_fields = [
        'certificate_id',
        'verification_url',
        'created_at',
        'updated_at',
        'email_sent_at',
        'drive_uploaded_at',
        'certificate_preview',
        'qr_code_preview',
        'verification_link'
    ]

    fieldsets = (
        ('Student Information', {
            'fields': ('full_name', 'course', 'college_name','affiliated_name', 'roll_number', 'email')
        }),
        ('Certificate Details', {
            'fields': ('certificate_id', 'verification_url', 'is_verified', 'notes')
        }),
        ('Files', {
            'fields': ('certificate_image', 'certificate_pdf', 'qr_code_image', 'certificate_preview', 'qr_code_preview')
        }),
        ('Email Status', {
            'fields': ('email_sent', 'email_sent_at')
        }),
        ('Google Drive Status', {
            'fields': ('drive_uploaded', 'drive_file_id', 'drive_uploaded_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    actions = ['send_email_certificates', 'upload_to_drive', 'regenerate_certificates','export_certificates_csv','export_certificates_zip']



    def certificate_id_short(self, obj):
        """Display shortened certificate ID"""
        return str(obj.certificate_id)[:8] + "..."
    certificate_id_short.short_description = "Cert ID"

    def certificate_preview(self, obj):
        """Display certificate image preview"""
        if obj.certificate_image:
            return format_html(
                '<img src="{}" style="max-width: 300px; max-height: 200px;" />',
                obj.certificate_image.url
            )
        return "No certificate image"
    certificate_preview.short_description = "Certificate Preview"

    def qr_code_preview(self, obj):
        """Display QR code preview"""
        if obj.qr_code_image:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px;" />',
                obj.qr_code_image.url
            )
        return "No QR code"
    qr_code_preview.short_description = "QR Code Preview"

    def verification_link(self, obj):
        """Display clickable verification link"""
        if obj.verification_url:
            return format_html(
                '<a href="{}" target="_blank">Verify Certificate</a>',
                obj.verification_url
            )
        return "No verification URL"
    verification_link.short_description = "Verification Link"

    def send_email_certificates(self, request, queryset):
        """Admin action to send email certificates"""
        from .utils import send_certificate_email

        sent_count = 0
        for certificate in queryset:
            if not certificate.email_sent and certificate.certificate_image:
                try:
                    send_certificate_email(certificate)
                    sent_count += 1
                except Exception as e:
                    self.message_user(request, f"Failed to send email for {certificate.full_name}: {str(e)}", level='ERROR')

        if sent_count > 0:
            self.message_user(request, f"Successfully sent {sent_count} certificate emails.")

    send_email_certificates.short_description = "Send certificate emails"

    def upload_to_drive(self, request, queryset):
        """Admin action to upload certificates to Google Drive"""
        from .utils import upload_to_google_drive

        uploaded_count = 0
        for certificate in queryset:
            if not certificate.drive_uploaded and certificate.certificate_image:
                try:
                    upload_to_google_drive(certificate)
                    uploaded_count += 1
                except Exception as e:
                    self.message_user(request, f"Failed to upload to Drive for {certificate.full_name}: {str(e)}", level='ERROR')

        if uploaded_count > 0:
            self.message_user(request, f"Successfully uploaded {uploaded_count} certificates to Google Drive.")

    upload_to_drive.short_description = "Upload to Google Drive"

    def regenerate_certificates(self, request, queryset):
        """Admin action to regenerate certificates"""
        from .utils import generate_certificate

        regenerated_count = 0
        for certificate in queryset:
            try:
                generate_certificate(certificate)
                regenerated_count += 1
            except Exception as e:
                self.message_user(request, f"Failed to regenerate certificate for {certificate.full_name}: {str(e)}", level='ERROR')

        if regenerated_count > 0:
            self.message_user(request, f"Successfully regenerated {regenerated_count} certificates.")

    regenerate_certificates.short_description = "Regenerate certificates"

    def export_certificates_csv(modeladmin, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename=certificates_{datetime.date.today()}.csv'

        writer = csv.writer(response)
        writer.writerow([
            'Full Name', 'Course', 'College Name', 'Roll Number', 'Affiliated Name',
            'Start Date', 'End Date', 'Email', 'Certificate ID', 'Verified',
            'Email Sent', 'Drive Uploaded', 'Created At'
        ])

        for cert in queryset:
             writer.writerow([
                cert.full_name, cert.course, cert.college_name, cert.roll_number,
                cert.affiliated_name, cert.start_date, cert.end_date,
                cert.email, cert.certificate_id, cert.is_verified,
                cert.email_sent, cert.drive_uploaded, cert.created_at
            ])

        return response
    export_certificates_csv.short_description=' Export'


    def export_certificates_zip(self, request, queryset):
        """
        Export certificate image files as a ZIP with the college name in the filename.
        """
        buffer = BytesIO()
        zip_file = zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED)

        for certificate in queryset:
            if certificate.certificate_image:
                file_path = certificate.certificate_image.path
                file_name = os.path.basename(file_path)
                zip_file.write(file_path, arcname=file_name)

        zip_file.close()
        buffer.seek(0)

        # Default to "certificates" if no valid data
        if queryset.exists():
            college_name = queryset.first().college_name or "college"
        else:
            college_name = "college"

        # Clean the college name to be safe for filenames
        safe_college_name = re.sub(r'\W+', '_', college_name.strip().lower())

        zip_filename = f"{safe_college_name}.zip"
        # zip_filename = f"{safe_college_name}_{datetime.date.today()}.zip"

        response = HttpResponse(buffer, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename={zip_filename}'
        return response


@admin.register(CertificateTemplate)
class CertificateTemplateAdmin(admin.ModelAdmin):
    """Admin interface for CertificateTemplate model"""

    list_display = [
        'name',
        'is_active',
        'font_size',
        'font_color',
        'created_at'
    ]

    list_filter = [
        'is_active',
        'created_at'
    ]

    search_fields = [
        'name'
    ]

    readonly_fields = [
        'created_at',
        'updated_at',
        'template_preview'
    ]

    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'template_image', 'is_active', 'template_preview')
        }),
        ('Text Positioning', {
            'fields': (
                ('name_x', 'name_y'),
                ('course_x', 'course_y'),
                ('college_x', 'college_y'),
                ('roll_x', 'roll_y'),
                ('cert_id_x', 'cert_id_y'),
                ('date_x', 'date_y'),
                ('qr_x', 'qr_y')
            )
        }),
        ('Font Settings', {
            'fields': ('font_size', 'font_color')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def template_preview(self, obj):
        """Display template image preview"""
        if obj.template_image:
            return format_html(
                '<img src="{}" style="max-width: 400px; max-height: 300px;" />',
                obj.template_image.url
            )
        return "No template image"
    template_preview.short_description = "Template Preview"



from django.contrib import admin
from .models import Certificate_student, CertificateExcelUpload
import pandas as pd
from django.utils.dateparse import parse_date

@admin.register(Certificate_student)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'course', 'roll_number','college_name','affiliated_name','start_date','end_date', 'email', 'created_at']



@admin.register(CertificateExcelUpload)
class CertificateExcelUploadAdmin(admin.ModelAdmin):
    list_display = ['excel_file', 'uploaded_at']
    actions = ['process_excel_file']

    def process_excel_file(self, request, queryset):
        for upload in queryset:
            df = pd.read_excel(upload.excel_file.path)

            for _, row in df.iterrows():
                Certificate_student.objects.get_or_create(
                    full_name=row['Name'],
                    course=row['Course'],
                    roll_number=row['Roll No'],
                    college_name=row['College Name'],
                    affiliated_name=row['Affiliated Name'],
                    start_date=parse_date(str(row['Start Date'])),
                    end_date=parse_date(str(row['End Date'])),
                    email=row['Email'],
                    contact=str(row['Contact']),
                    gender=row['Gender']
                )
        self.message_user(request, "Certificates imported successfully.")
    process_excel_file.short_description = "Process and import certificate data"



