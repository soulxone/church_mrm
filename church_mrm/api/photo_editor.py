import frappe
import os
import time
from PIL import Image, ImageOps

# Register HEIC/HEIF support if available
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass

SUPPORTED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".heic", ".heif"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@frappe.whitelist()
def process_photo(file_url, crop_x=0, crop_y=0, crop_width=0, crop_height=0,
                  rotate=0, resize_width=0, resize_height=0,
                  doctype=None, docname=None):
    """Process a photo with rotate, crop, and resize operations using Pillow."""

    if doctype and docname:
        frappe.has_permission(doctype, "write", doc=docname, throw=True)

    # Cast params (arrive as strings from HTTP)
    crop_x = int(float(crop_x))
    crop_y = int(float(crop_y))
    crop_width = int(float(crop_width))
    crop_height = int(float(crop_height))
    rotate = int(float(rotate))
    resize_width = int(float(resize_width))
    resize_height = int(float(resize_height))

    # Resolve file path
    file_path = resolve_file_path(file_url)
    if not file_path or not os.path.exists(file_path):
        frappe.throw("File not found: {}".format(file_url))

    # Check extension
    ext = os.path.splitext(file_path)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        frappe.throw("Unsupported image format: {}. Supported: {}".format(
            ext, ", ".join(SUPPORTED_EXTENSIONS)))

    # Check file size
    if os.path.getsize(file_path) > MAX_FILE_SIZE:
        frappe.throw("File too large. Maximum size is 10MB.")

    # Process image
    img = Image.open(file_path)

    # Normalize EXIF orientation (critical for phone photos)
    img = ImageOps.exif_transpose(img)

    # 1. Rotate (Cropper.js uses clockwise-positive, Pillow counter-clockwise)
    if rotate:
        img = img.rotate(-rotate, expand=True)

    # 2. Crop
    if crop_width > 0 and crop_height > 0:
        # Clamp to image bounds
        img_w, img_h = img.size
        x1 = max(0, crop_x)
        y1 = max(0, crop_y)
        x2 = min(img_w, crop_x + crop_width)
        y2 = min(img_h, crop_y + crop_height)
        if x2 > x1 and y2 > y1:
            img = img.crop((x1, y1, x2, y2))

    # 3. Resize
    if resize_width > 0 or resize_height > 0:
        orig_w, orig_h = img.size
        if resize_width > 0 and resize_height > 0:
            new_size = (resize_width, resize_height)
        elif resize_width > 0:
            ratio = resize_width / orig_w
            new_size = (resize_width, int(orig_h * ratio))
        else:
            ratio = resize_height / orig_h
            new_size = (int(orig_w * ratio), resize_height)
        img = img.resize(new_size, Image.LANCZOS)

    # Determine output format (HEIC -> JPEG)
    out_ext = ext
    if ext in (".heic", ".heif"):
        out_ext = ".jpg"

    # Convert RGBA to RGB for JPEG
    if out_ext in (".jpg", ".jpeg") and img.mode == "RGBA":
        img = img.convert("RGB")

    # Generate output filename
    original_stem = os.path.splitext(os.path.basename(file_path))[0]
    # Strip previous _edited_ suffixes
    if "_edited_" in original_stem:
        original_stem = original_stem.split("_edited_")[0]
    timestamp = int(time.time())
    new_filename = "{}_edited_{}{}".format(original_stem, timestamp, out_ext)

    # Save to public files
    site_path = frappe.get_site_path("public", "files")
    new_file_path = os.path.join(site_path, new_filename)

    save_kwargs = {}
    if out_ext in (".jpg", ".jpeg"):
        save_kwargs = {"quality": 90, "optimize": True}
    elif out_ext == ".png":
        save_kwargs = {"optimize": True}
    elif out_ext == ".webp":
        save_kwargs = {"quality": 90}

    img.save(new_file_path, **save_kwargs)

    new_file_url = "/files/{}".format(new_filename)

    # Create Frappe File doc
    file_doc = frappe.get_doc({
        "doctype": "File",
        "file_url": new_file_url,
        "file_name": new_filename,
        "is_private": 0,
        "attached_to_doctype": doctype,
        "attached_to_name": docname,
    })
    file_doc.insert(ignore_permissions=True)

    # Clean up previous edited versions (not the original)
    cleanup_old_edits(file_url, new_file_url, doctype, docname)

    return {"file_url": new_file_url}


def resolve_file_path(file_url):
    """Resolve a Frappe file URL to an absolute disk path."""
    if not file_url:
        return None

    if file_url.startswith("/private/files/"):
        return frappe.get_site_path("private", "files",
                                     file_url.replace("/private/files/", ""))
    elif file_url.startswith("/files/"):
        return frappe.get_site_path("public", "files",
                                     file_url.replace("/files/", ""))
    else:
        # Try looking up via File doctype
        file_doc = frappe.db.get_value("File", {"file_url": file_url},
                                        ["file_url"], as_dict=True)
        if file_doc:
            return resolve_file_path(file_doc.file_url)
    return None


def cleanup_old_edits(current_url, new_url, doctype, docname):
    """Delete previous _edited_ versions to prevent file accumulation."""
    if not (doctype and docname):
        return

    # Only clean up if the current file was itself an edit
    if "_edited_" not in (current_url or ""):
        return

    try:
        old_files = frappe.get_all("File", filters={
            "file_url": current_url,
            "attached_to_doctype": doctype,
            "attached_to_name": docname,
        }, pluck="name")

        for fname in old_files:
            fdoc = frappe.get_doc("File", fname)
            fdoc.delete(ignore_permissions=True)
    except Exception:
        # Don't fail the edit if cleanup fails
        pass
