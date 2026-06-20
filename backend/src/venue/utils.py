import re    
from django.utils.text import slugify


def generate_unique_slug(model_class, name, pk=None):
    base_slug = slugify(name)

    existing_slugs = model_class.objects.filter(
        slug__regex=rf"^{re.escape(base_slug)}(-[0-9]+)?$"
    ).values_list("slug", flat=True)

    if base_slug not in existing_slugs:
        return base_slug
    new_slug = f"{base_slug}-{str(pk).split("-")[-1]}"
    return new_slug

def venue_image_upload_path(instance, filename):
    return f"venues/{instance.venue_id}/images/{filename}"