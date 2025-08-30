#!/usr/bin/env python3.11
"""
Test script for certificate generation
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.append('/home/ubuntu/certificate_system')

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'certificate_project.settings')
django.setup()

from certificates.models import Certificate
from certificates.utils import generate_certificate, create_certificate_from_form_data

def test_certificate_generation():
    """Test certificate generation with sample data"""
    print("Testing certificate generation...")
    
    # Sample form data
    form_data = {
        'full_name': 'John Doe',
        'course': 'Python Programming',
        'college_name': 'Tech University',
        'roll_number': 'CS2024001',
        'email': 'john.doe@example.com'
    }
    
    try:
        # Create certificate
        certificate = create_certificate_from_form_data(form_data)
        print(f"Certificate created successfully!")
        print(f"Certificate ID: {certificate.certificate_id}")
        print(f"Verification URL: {certificate.verification_url}")
        print(f"Certificate Image: {certificate.certificate_image.url if certificate.certificate_image else 'Not generated'}")
        print(f"QR Code Image: {certificate.qr_code_image.url if certificate.qr_code_image else 'Not generated'}")
        
        return certificate
        
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_certificate_generation()

