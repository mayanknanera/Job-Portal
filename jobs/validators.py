from django.core.exceptions import ValidationError

ALLOWED_EXTENSIONS = ["pdf", "doc", "docx"]
MAX_FILE_SIZE_MB = 5


def validate_resume(file):
    # Validate file extension
    extension = file.name.split(".")[-1].lower()
    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            "Invalid file type. Only PDF and Word documents are allowed."
        )

    # Validate file size
    if file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise ValidationError(
            f"File size must be under {MAX_FILE_SIZE_MB} MB."
        )
