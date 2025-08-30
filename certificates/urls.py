from django.urls import path
from . import views
from django.views.generic import RedirectView
from django.http import HttpResponse

def google_verification(request):
    return HttpResponse("google-site-verification: google123456789abcd.html")
def sitemap_view(request):
    xml = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
   <url>
      <loc>https://verify.cscindia.org.in/</loc>
      <lastmod>2025-08-01</lastmod>
      <priority>1.0</priority>
   </url>
</urlset>"""
    return HttpResponse(xml, content_type="application/xml")
    
urlpatterns = [
    # Main pages
    path("google123456789abcd.html", google_verification),
    path("sitemap.xml", sitemap_view),
    path('favicon.ico', RedirectView.as_view(url='/static/favicon.ico', permanent=True)),
    path('home', views.home, name='home'),
    path('', views.verify_student, name='verify_student'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('page_not_found /', views.page_not_found , name='page_not_found'),
    path('generate/', views.generate_certificate, name='generate_certificate'),
    path('certificates/', views.certificate_list, name='certificate_list'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('stats/', views.stats, name='stats'),
    path('upload/', views.upload_excel, name='upload_excel'),
    path('generate-from-db/', views.generate_certificates_from_db, name='generate_certificates_from_db'),
    path('certificates/export/', views.export_certificates, name='export_certificates'),
    path('certificate/<str:certificate_id>/', views.certificate_detail, name='certificate_detail'),
    path('verify/<str:certificate_id>/', views.verify_certificate, name='verify_certificate'),
    path('download_excel_template/', views.download_excel_template, name='download_excel_template'),
    
    # Download endpoints
    path('download/<str:certificate_id>/', views.download_certificate, name='download_certificate'),
    path('download-pdf/<str:certificate_id>/', views.download_certificate_pdf, name='download_certificate_pdf'),
    
    # API endpoints
    path('api/verify/<str:certificate_id>/', views.api_verify_certificate, name='api_verify_certificate'),


]

