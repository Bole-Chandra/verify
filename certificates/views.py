from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, HttpResponse, Http404
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db.models import Q
from django.conf import settings
import json
import logging

from .models import Certificate
from .forms import CertificateForm, CertificateSearchForm, ContactForm
from .utils import process_certificate_request

logger = logging.getLogger(__name__)
from django.http import Http404,HttpResponse
from functools import wraps

def login_required_404(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
           return redirect("page_not_found")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def page_not_found(request):
    return render(request, 'certificates/page_not_found.html', )

from django.contrib.auth.decorators import login_required
@login_required_404
def home(request):
    """Home page view"""
    recent_certificates = Certificate.objects.filter(is_verified=True)[:6]
    stats = {
        'total_certificates': Certificate.objects.count(),
        'verified_certificates': Certificate.objects.filter(is_verified=True).count(),
        'emails_sent': Certificate.objects.filter(email_sent=True).count(),
    }

    context = {
        'recent_certificates': recent_certificates,
        'stats': stats,
    }
    return render(request, 'certificates/home.html', context)
    
@login_required_404
def generate_certificate(request):
    """Certificate generation form view"""
    if request.method == 'POST':
        form = CertificateForm(request.POST)
        if form.is_valid():
            roll_number = form.cleaned_data.get('roll_number')
            if Certificate.objects.filter(roll_number=roll_number).exists():
                messages.error(request, f'A certificate has already been generated for roll number: {roll_number}. Duplicate certificates are not allowed.')
            else:
                try:
                    # Process certificate request
                    certificate = process_certificate_request(form.cleaned_data)
                    # Success message
                    messages.success(
                        request, 
                        f'Certificate generated successfully! Certificate ID: {certificate.certificate_id}'
                    )
                    # Redirect to certificate detail page
                    return redirect('certificate_detail', certificate_id=certificate.certificate_id)
                except Exception as e:
                    logger.error(f"Error generating certificate: {str(e)}")
                    messages.error(
                        request, 
                        'An error occurred while generating your certificate. Please try again.'
                    )
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CertificateForm()
    context = {
        'form': form,
        'page_title': 'Generate Certificate',
    }
    return render(request, 'certificates/generate.html', context)



@login_required_404
def certificate_detail(request, certificate_id):
    """Certificate detail view"""
    try:
        certificate = get_object_or_404(Certificate, certificate_id=certificate_id)

        context = {
            'certificate': certificate,
            'page_title': f'Certificate - {certificate.full_name}',
        }
        return render(request, 'certificates/detail.html', context)

    except Exception as e:
        logger.error(f"Error loading certificate detail: {str(e)}")
        raise Http404("Certificate not found")


def verify_certificate(request, certificate_id):
    """Certificate verification view"""
    try:
        certificate = get_object_or_404(Certificate, certificate_id=certificate_id)

        context = {
            'certificate': certificate,
            'is_verified': certificate.is_verified,
            'page_title': 'Certificate Verification',
        }
        return render(request, 'certificates/verify.html', context)

    except Exception as e:
        logger.error(f"Error verifying certificate: {str(e)}")
        context = {
            'certificate': None,
            'is_verified': False,
            'page_title': 'Certificate Verification',
            'error_message': 'Certificate not found or invalid.'
        }
        return render(request, 'certificates/verify.html', context)

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
import pandas as pd
from .models import Certificate
from .forms import CertificateSearchForm
from django.db.models.functions import Lower
@login_required_404
def certificate_list(request):
    form = CertificateSearchForm(request.GET or None)
    certificates = Certificate.objects.filter(is_verified=True).order_by('-created_at')
    courses_qs = Certificate.objects.annotate(
    course_lower=Lower('course')).values_list('course_lower', flat=True).order_by('course_lower').distinct()
    colleges_qs = Certificate.objects.annotate(
    college_lower=Lower('college_name')).values_list('college_lower', flat=True).order_by('college_lower').distinct()
    courses = [course.title() for course in courses_qs]
    colleges = [college.title() for college in colleges_qs]
    search_query = request.GET.get('search_query', '')
    course_filter = request.GET.get('course_filter', '')
    college_filter = request.GET.get('college_filter', '')

    if search_query:
        certificates = certificates.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(roll_number__icontains=search_query) |
            Q(certificate_id__icontains=search_query)
        )

    if course_filter:
        certificates = certificates.filter(course__icontains=course_filter)

    if college_filter:
        certificates = certificates.filter(college_name__icontains=college_filter)

    paginator = Paginator(certificates, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'form': form,
        'page_obj': page_obj,
        'certificates': page_obj,
        'courses': courses,
        'colleges': colleges,
        'search_query': search_query,
        'course_filter': course_filter,
        'college_filter': college_filter,
        'is_paginated':paginator,
    }
    return render(request, 'certificates/list.html', context)
def export_certificates(request):
    search_query = request.GET.get('search_query', '').strip()
    course_filter = request.GET.get('course_filter', '').strip()
    college_filter = request.GET.get('college_filter', '').strip()

    certificates = Certificate.objects.filter(is_verified=True)

    if search_query:
        certificates = certificates.filter(
            Q(full_name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(roll_number__icontains=search_query) |
            Q(certificate_id__icontains=search_query)
        )

    if course_filter:
        certificates = certificates.filter(course__iexact=course_filter)

    if college_filter:
        certificates = certificates.filter(college_name__iexact=college_filter)

    if not certificates.exists():
        messages.warning(request, "No certificate data found for the selected filters.")
        return redirect('certificate_list')

    # Export to Excel
    data = []
    for cert in certificates:
        data.append({
            'Full Name': cert.full_name,
            'Email': cert.email,
            'Roll Number': cert.roll_number,
            'College': cert.college_name,
            'Course': cert.course,
            'Certificate ID': cert.certificate_id,
            'Verified': 'Yes' if cert.is_verified else 'No',
            'Email Sent': 'Yes' if cert.email_sent else 'No',
            'Drive Uploaded': 'Yes' if cert.drive_uploaded else 'No',
            'Issued Date': cert.created_at.strftime('%d-%m-%Y'),
        })

    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=Filtered_Certificates.xlsx'

    with pd.ExcelWriter(response, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Certificates')

    return response






def download_certificate(request, certificate_id):
    """Download certificate image"""
    try:
        certificate = get_object_or_404(Certificate, certificate_id=certificate_id)

        if not certificate.certificate_image:
            raise Http404("Certificate image not found")

        # Serve the file
        response = HttpResponse(
            certificate.certificate_image.read(),
            content_type='image/png'
        )
        response['Content-Disposition'] = f'attachment; filename="{certificate.roll_number.replace(" ", "_")}.png"'

        return response

    except Exception as e:
        logger.error(f"Error downloading certificate: {str(e)}")
        raise Http404("Certificate not found")


def download_certificate_pdf(request, certificate_id):
    """Download certificate PDF"""
    try:
        certificate = get_object_or_404(Certificate, certificate_id=certificate_id)

        if not certificate.certificate_pdf:
            raise Http404("Certificate PDF not found")

        # Serve the file
        response = HttpResponse(
            certificate.certificate_pdf.read(),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{certificate.roll_number.replace(" ", "_")}.pdf"'

        return response

    except Exception as e:
        logger.error(f"Error downloading certificate PDF: {str(e)}")
        raise Http404("Certificate PDF not found")


@require_http_methods(["GET", "POST"])
def contact(request):
    """Contact form view"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            try:
                # Here you would typically send an email or save to database
                # For now, just show a success message
                messages.success(
                    request,
                    'Thank you for your message! We will get back to you soon.'
                )
                return redirect('contact')
            except Exception as e:
                logger.error(f"Error processing contact form: {str(e)}")
                messages.error(
                    request,
                    'An error occurred while sending your message. Please try again.'
                )
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()

    context = {
        'form': form,
        'page_title': 'Contact Us',
    }
    return render(request, 'certificates/contact.html', context)


def about(request):
    """About page view"""
    context = {
        'page_title': 'About Us',
    }
    return render(request, 'certificates/about.html', context)


@csrf_exempt
def api_verify_certificate(request, certificate_id):
    """API endpoint for certificate verification"""
    if request.method != 'GET':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        certificate = Certificate.objects.get(certificate_id=certificate_id)

        data = {
            'verified': certificate.is_verified,
            'certificate_id': str(certificate.certificate_id),
            'full_name': certificate.full_name,
            'course': certificate.course,
            'college_name': certificate.college_name,
            'roll_number': certificate.roll_number,
            'issue_date': certificate.created_at.strftime('%d %B %Y'),
            'verification_url': certificate.verification_url,
        }

        return JsonResponse(data)

    except Certificate.DoesNotExist:
        return JsonResponse({
            'verified': False,
            'error': 'Certificate not found'
        }, status=404)
    except Exception as e:
        logger.error(f"API verification error: {str(e)}")
        return JsonResponse({
            'verified': False,
            'error': 'Verification failed'
        }, status=500)

@login_required_404
def stats(request):
    """Statistics page"""
    stats_data = {
        'total_certificates': Certificate.objects.count(),
        'verified_certificates': Certificate.objects.filter(is_verified=True).count(),
        'emails_sent': Certificate.objects.filter(email_sent=True).count(),
        'drive_uploads': Certificate.objects.filter(drive_uploaded=True).count(),
        'recent_certificates': Certificate.objects.filter(is_verified=True).order_by('-created_at')[:10],
        'top_courses': Certificate.objects.order_by(Lower('course')).values_list('course', flat=True).distinct(),
        'top_colleges': Certificate.objects.order_by(Lower('college_name')).values_list('college_name', flat=True).distinct(),
    }

    context = {
        'stats': stats_data,
        'page_title': 'Statistics',
    }
    return render(request, 'certificates/stats.html', context)


from django.shortcuts import render, redirect
from .forms import CertificateExcelForm
from .models import Certificate_student
import pandas as pd
from django.contrib import messages
from django.utils.dateparse import parse_date

@login_required_404
def upload_excel(request):
    if request.method == 'POST':
        form = CertificateExcelForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save()
            df = pd.read_excel(instance.excel_file.path)

            for _, row in df.iterrows():
                Certificate_student.objects.create(
                    full_name=row['Name'],
                    course=row['Course'],
                    roll_number=row['Roll No'],
                    college_name=row['College Name'],
                    affiliated_name=row['Affiliated Name'],
                    start_date=row['Start Date'],
                    end_date=row['End Date'],

                    email=row['Email'],
                    contact=str(row.get('Contact', 'NONE')) if pd.notna(row.get('Contact')) else 'NONE',
                    gender=row.get('Gender', 'NONE') if pd.notna(row.get('Gender')) else 'NONE'
                )

            messages.success(request, "Excel file uploaded and all records added to the database.")
            return redirect('upload_excel')
    else:
        form = CertificateExcelForm()

    return render(request, 'certificates/upload_excel.html', {'form': form})

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Certificate_student
from .utils import process_certificate_request, send_certificate_email, upload_to_google_drive
import logging

logger = logging.getLogger(__name__)
@login_required_404
def generate_certificates_from_db(request):
    """
    Bulk generate certificates from Certificate_student model.
    Successfully processed rows will be deleted from the database.
    """
    if request.method == 'POST':
        students = Certificate_student.objects.all()
        success_count = 0
        fail_count = 0
        duplicate_count = 0  # Track duplicates
        if not students.exists():
            messages.warning(request, "⚠️ No data found. Please insert student details before generating certificates.")
            return redirect('generate_certificates_from_db')
        
        selected_template = request.POST.get('template') or request.session.get('bulk_selected_template', 'Pragna')
        for student in students:
            try:
                # Check for duplicate roll number
                if Certificate.objects.filter(roll_number=student.roll_number).exists():
                    logger.info(f"Certificate already exists for roll number: {student.roll_number}. Skipping.")
                    duplicate_count += 1
                    continue

                data = {
                    'full_name': student.full_name.upper(),
                    'course': student.course,
                    'roll_number': student.roll_number,
                    'college_name': student.college_name,
                    'affiliated_name': student.affiliated_name,
                    'start_date': student.start_date,
                    'end_date': student.end_date,
                    'email': student.email,
                    'template': selected_template,
                }

                # Step 1: Generate the certificate
                certificate = process_certificate_request(data)

                # If successful, delete the student entry
                student.delete()

                success_count += 1

            except Exception as e:
                logger.error(f"Error for {student.full_name}: {str(e)}")
                fail_count += 1

        messages.success(
            request,
            f"✅ {success_count} certificates generated. ❌ {fail_count} failed and were retained. 🚫 {duplicate_count} skipped due to duplicate roll numbers."
        )
        return redirect('generate_certificates_from_db')

    return render(request, 'certificates/generate_from_db.html', {
        'page_title': 'Generate Certificates from Uploaded Data',
    })



import pandas as pd
from django.http import HttpResponse
from .models import Certificate_student
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username').strip()
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # change to your homepage/dashboard URL name
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'login.html')
def logout_view(request):
    logout(request)
    return redirect('verify_student')  # Redirect to login page after logout

from django.http import FileResponse, Http404
from .models import CertificateExcelUpload  # adjust the import as per your structure
def download_excel_template(request):
    try:
        # Filter for exact filename (case-sensitive)
        template_obj = CertificateExcelUpload.objects.get(excel_file__icontains='EXCEL_TEMPLATE_KC7h9YF.xlsx')
        return FileResponse(template_obj.excel_file.open('rb'), as_attachment=True, filename='EXCEL_TEMPLATE.xlsx')
    except CertificateExcelUpload.DoesNotExist:
        raise Http404("Excel template named 'EXCEL_TEMPLATE.xlsx' not found.")




from django.shortcuts import render
from django.db.models import Q
from .models import Certificate  # Make sure this import is correct

def verify_student(request):
    """
    Public certificate verification page supporting multiple methods.
    Accepts GET params: method (certificate_id, phone, email, roll_number), value (user input).
    Renders result in certificates/verify_student.html.
    """
    method = request.GET.get('method', 'certificate_id')
    value = request.GET.get('value', '').strip()
    certificate = None
    is_verified = False
    error_message = ''
    verification_attempted = False  # NEW FLAG

    if value:
        verification_attempted = True  # Mark that verification was attempted
        query = Q()
        
        if method == 'certificate_id':
            query = Q(certificate_id__iexact=value)
        elif method == 'phone':
            query = Q(phone__icontains=value)  # Assumes a phone field exists
        elif method == 'email':
            query = Q(email__iexact=value)
        elif method == 'roll_number':
            query = Q(roll_number__iexact=value)
        else:
            error_message = 'Invalid verification method.'

        if not error_message:
            try:
                certificate = Certificate.objects.filter(query, is_verified=True).first()
                if certificate:
                    is_verified = True
                else:
                    error_message = 'No certificate found for the provided information.'
            except Exception as e:
                error_message = 'An error occurred during verification.'

    context = {
        'certificate': certificate,
        'is_verified': is_verified,
        'error_message': error_message,
        'method': method,
        'value': value,
        'verification_attempted': verification_attempted,  # PASS TO TEMPLATE
    }

    return render(request, 'certificates/verify_student.html', context)


