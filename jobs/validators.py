from django.core.exceptions import ValidationError

# ─── Resume Upload Rules ──────────────────────────────────────────────────────

ALLOWED_EXTENSIONS = ["pdf", "doc", "docx"]  # accepted file types
MAX_FILE_SIZE_MB   = 5                        # maximum file size in megabytes


def validate_resume(file):
    """
    Validates a resume file upload.
    Raises a ValidationError if:
    - The file extension is not PDF, DOC, or DOCX
    - The file is larger than 5 MB
    """
    # Check file extension
    extension = file.name.split(".")[-1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            "Invalid file type. Only PDF and Word documents are allowed."
        )

    # Check file size (convert MB limit to bytes for comparison)
    if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise ValidationError(
            f"File size must be under {MAX_FILE_SIZE_MB} MB."
        )
