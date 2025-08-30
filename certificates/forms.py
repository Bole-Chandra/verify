from django import forms
from django.core.validators import RegexValidator
from .models import Certificate


class CertificateForm(forms.Form):
    """Form for certificate generation"""

    full_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your full name',
            'required': True
        }),
        help_text='Enter your full name as it should appear on the certificate'
    )

    course = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter course name',
            'required': True
        }),
        help_text='Enter the course name'
    )

    college_name = forms.CharField(
        max_length=300,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter college/institution name',
            'required': True
        }),
        help_text='Enter the name of your college or institution'
    )
    affiliated_name= forms.CharField(
        max_length=300,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Affiliated University name',
            'required': True
        }),
        help_text='Enter the name of your Affiliated University'
    )

    roll_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your roll number',
            'required': True
        }),
        help_text='Enter your student roll number'
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your email address',
            'required': True
        }),
        help_text='Enter your email address to receive the certificate'
    )
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',  # enables date picker in HTML5 browsers
            'required': True
        }),
        help_text='Select the start date of the course'
    )

    end_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'required': True
        }),
        help_text='Select the end date of the course'
    )
    template = forms.ChoiceField(
        choices=[
            ("Pragna", "Pragna"),
            ("CSCIndia", "CSCIndia"),
            ("DataValley", "DataValley"),
            ("IGIATPragna", "IGIATPragna"),
            ("UrChoice", "UrChoice"),
            ("Proplore", "Proplore"),
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True,
        help_text='Select the certificate template',
        initial="DataValley"
    )

    def clean_full_name(self):
        """Validate full name"""
        full_name = self.cleaned_data.get('full_name')
        if not full_name:
            raise forms.ValidationError('Full name is required')

        # Check for minimum length
        if len(full_name.strip()) < 2:
            raise forms.ValidationError('Full name must be at least 2 characters long')

        # Check for valid characters (letters, spaces, hyphens, apostrophes)
        if not all(c.isalpha() or c.isspace() or c in "'-." for c in full_name):
            raise forms.ValidationError('Full name can only contain letters, spaces, hyphens, apostrophes, and periods')

        return full_name.strip().title()

    def clean_course(self):
        """Validate course name"""
        course = self.cleaned_data.get('course')
        if not course:
            raise forms.ValidationError('Course name is required')

        if len(course.strip()) < 2:
            raise forms.ValidationError('Course name must be at least 2 characters long')

        return course.strip()

    def clean_college_name(self):
        """Validate college name"""
        college_name = self.cleaned_data.get('college_name')
        if not college_name:
            raise forms.ValidationError('College name is required')

        if len(college_name.strip()) < 2:
            raise forms.ValidationError('College name must be at least 2 characters long')

        return college_name.strip()

    def clean_roll_number(self):
        """Validate roll number"""
        roll_number = self.cleaned_data.get('roll_number')
        if not roll_number:
            raise forms.ValidationError('Roll number is required')

        roll_number = roll_number.strip().upper()

        # Check for minimum length
        if len(roll_number) < 3:
            raise forms.ValidationError('Roll number must be at least 3 characters long')

        return roll_number

    def clean_email(self):
        """Validate email and check for duplicates"""
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError('Email address is required')

        email = email.lower().strip()

        # Check if certificate already exists for this email and course combination
        # (Optional: You might want to allow multiple certificates per email)

        return email


class CertificateSearchForm(forms.Form):
    """Form for searching certificates"""

    search_query = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by name, email, roll number, or certificate ID',
        }),
        help_text='Enter search terms to find certificates'
    )

    course_filter = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by course name',
        }),
        help_text='Filter certificates by course name'
    )

    college_filter = forms.CharField(
        max_length=300,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Filter by college name',
        }),
        help_text='Filter certificates by college name'
    )


class ContactForm(forms.Form):
    """Contact form for support"""

    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your name',
            'required': True
        })
    )

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your email address',
            'required': True
        })
    )

    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Subject',
            'required': True
        })
    )

    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'placeholder': 'Your message',
            'rows': 5,
            'required': True
        })
    )

from django import forms
from .models import CertificateExcelUpload

class CertificateExcelForm(forms.ModelForm):
    class Meta:
        model = CertificateExcelUpload
        fields = ['excel_file']
        widgets = {
            'excel_file': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
