from django.core.files.base import ContentFile
from django.template.loader import render_to_string
from weasyprint import HTML
from io import BytesIO

from .course_models import CourseCertificate

class CertificatePDFService:
    """Servicio para generar PDF de certificados de curso usando HTML.
    
    Genera un PDF renderizando el template HTML del certificado con WeasyPrint.
    """

    def generate_pdf(self, certificate: CourseCertificate, regenerate: bool = False) -> CourseCertificate:
        if certificate.pdf_file and not regenerate:
            return certificate  # Ya existe

        # Renderizar el template HTML
        html_content = render_to_string('educational/certificate_pdf.html', {
            'certificate': certificate,
        })
        
        # Convertir HTML a PDF usando WeasyPrint
        pdf_file = HTML(string=html_content).write_pdf()
        
        # Guardar el PDF
        filename = f"certificado_{certificate.certificate_code}.pdf".lower()
        certificate.pdf_file.save(filename, ContentFile(pdf_file), save=True)
        
        return certificate
