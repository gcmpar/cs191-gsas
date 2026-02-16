from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Applicant, TORText
import pypdf
import logging

logger = logging.getLogger(__name__)

@receiver(post_save, sender=Applicant)
def extract_pdf_text(sender, instance, created, **kwargs):
    if instance.pdf_file:
        try:
            # Check if file exists and is accessible
            if not instance.pdf_file.path:
                logger.warning(f"No file path found for applicant {instance.applicant_id}")
                return

            extracted_text = ""
            with instance.pdf_file.open('rb') as f:
                reader = pypdf.PdfReader(f)
                for page in reader.pages:
                    extracted_text += page.extract_text() + "\n"
            
            # Create or update TORText entry
            TORText.objects.update_or_create(
                applicant=instance,
                defaults={'text': extracted_text}
            )
            logger.info(f"Successfully extracted text for applicant {instance.applicant_id}")
            
        except Exception as e:
            logger.error(f"Error extracting text for applicant {instance.applicant_id}: {str(e)}")
