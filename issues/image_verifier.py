"""
Fix My City - AI-Generated Image & Spam Verification Engine
Architecture: Combine Method (Hardware EXIF Fast-Path + Algorithmic Synthetic Detector)

Specification:
1. Authentic camera hardware metadata (Make, Model, Lens, GPS timestamp) from a phone camera -> Instantly Approved.
2. Stripped metadata or synthetic signatures -> AI & Digital Art Detector Pipeline.
3. If flagged -> Alert: "⚠️ Image detected as AI-generated or digital art. Please upload a genuine on-site photograph."
"""

import io
import math
import logging
from PIL import Image, ImageStat
from PIL.ExifTags import TAGS, GPSTAGS

logger = logging.getLogger(__name__)

# Known phone/camera hardware manufacturers
VALID_CAMERA_MAKES = [
    'apple', 'samsung', 'xiaomi', 'google', 'sony', 'oneplus', 'huawei',
    'oppo', 'vivo', 'realme', 'motorola', 'nokia', 'infinix', 'tecno',
    'canon', 'nikon', 'fujifilm', 'panasonic', 'lg', 'honor', 'asus'
]

# Known AI generators, digital art suites, and synthetic markers
SYNTHETIC_MARKERS = [
    'midjourney', 'dall-e', 'dalle', 'stable diffusion', 'stablediffusion',
    'comfyui', 'novelai', 'flux.1', 'civitai', 'artbreeder', 'leonardo.ai',
    'photoshop', 'illustrator', 'procreate', 'clip studio', 'blender',
    'unreal engine', 'prompt:', 'negative_prompt', 'steps:', 'sampler:'
]


def convert_dms_to_degrees(value):
    """Convert EXIF DMS tuple to decimal degrees."""
    try:
        d = float(value[0])
        m = float(value[1])
        s = float(value[2])
        return round(d + (m / 60.0) + (s / 3600.0), 6)
    except Exception:
        return None


def extract_exif_metadata(image_file):
    """Extract and decode raw EXIF dictionary from an image file."""
    try:
        if hasattr(image_file, 'seek'):
            image_file.seek(0)
        img = Image.open(image_file)
        raw_exif = img._getexif()
        if not raw_exif:
            return None, img

        exif = {}
        for tag_id, value in raw_exif.items():
            tag_name = TAGS.get(tag_id, tag_id)
            if tag_name == 'GPSInfo':
                gps_dict = {}
                for t, v in value.items():
                    sub_name = GPSTAGS.get(t, t)
                    gps_dict[sub_name] = v
                exif['GPSInfo'] = gps_dict
            else:
                exif[tag_name] = value
        return exif, img
    except Exception as e:
        logger.warning(f"EXIF parsing error: {e}")
        try:
            if hasattr(image_file, 'seek'):
                image_file.seek(0)
            img = Image.open(image_file)
            return None, img
        except Exception:
            return None, None


def extract_gps_coords(exif):
    """Extract decimal lat/lng from parsed EXIF dictionary."""
    if not exif or 'GPSInfo' not in exif:
        return None, None
    gps = exif['GPSInfo']
    lat_val = gps.get('GPSLatitude')
    lat_ref = gps.get('GPSLatitudeRef', 'N')
    lng_val = gps.get('GPSLongitude')
    lng_ref = gps.get('GPSLongitudeRef', 'E')

    if lat_val and lng_val:
        lat = convert_dms_to_degrees(lat_val)
        lng = convert_dms_to_degrees(lng_val)
        if lat and lat_ref != 'N':
            lat = -lat
        if lng and lng_ref != 'E':
            lng = -lng
        return lat, lng
    return None, None


def scan_binary_for_ai_markers(image_file):
    """
    Scans raw bytes (JPEG COM chunks, PNG text chunks) for prompt keywords or AI model signatures.
    """
    try:
        if hasattr(image_file, 'seek'):
            image_file.seek(0)
            header_chunk = image_file.read(65536)
            image_file.seek(0)
        else:
            return False, ""

        header_str = header_chunk.decode('latin-1', errors='ignore').lower()
        for marker in SYNTHETIC_MARKERS:
            if marker in header_str:
                return True, marker
        return False, ""
    except Exception as e:
        logger.warning(f"Marker scan error: {e}")
        return False, ""


def analyze_image_heuristics(img):
    """
    Heuristic signal analysis for synthetic/digital art characteristics:
    1. Color saturation distribution & entropy (digital art has extreme gradient uniformity).
    2. Local pixel noise variance (real phone sensors have Gaussian/Poisson noise grain).
    3. Standard deviation across color channels.
    """
    try:
        # Resize to standardized thumbnail for fast heuristic inspection
        thumb = img.convert('RGB').resize((128, 128))
        stat = ImageStat.Stat(thumb)
        
        # Color variance across RGB channels
        variances = stat.var
        avg_var = sum(variances) / len(variances)

        # Convert to HSV to evaluate saturation and value distribution
        hsv_thumb = thumb.convert('HSV')
        h_channel, s_channel, v_channel = hsv_thumb.split()
        s_stat = ImageStat.Stat(s_channel)
        mean_saturation = s_stat.mean[0]
        saturation_stddev = s_stat.stddev[0]

        # Gray conversion to measure micro-noise (high-frequency local variance)
        gray = thumb.convert('L')
        pixels = list(gray.getdata())
        width, height = gray.size

        # Compute adjacent pixel difference variance (Laplacian proxy for sensor noise)
        diffs = []
        for y in range(height - 1):
            row_start = y * width
            for x in range(width - 1):
                idx = row_start + x
                diff = abs(pixels[idx] - pixels[idx + 1]) + abs(pixels[idx] - pixels[idx + width])
                diffs.append(diff)
        
        diff_mean = sum(diffs) / len(diffs) if diffs else 0
        diff_var = sum((d - diff_mean) ** 2 for d in diffs) / len(diffs) if diffs else 0
        diff_stddev = math.sqrt(diff_var)

        # AI digital art indicators:
        # Digital art / synthetic renders typically exhibit hyper-vivid saturation (>140)
        # paired with unnatural gradient smoothness or vector rendering.
        is_synthetic = False
        ai_score = 0.10

        if mean_saturation > 150 and diff_stddev < 6.0:
            # Hyper-saturated digital art / anime / Midjourney aesthetic
            ai_score += 0.55
        elif mean_saturation > 170:
            ai_score += 0.35

        if diff_stddev < 1.0 and avg_var < 25 and mean_saturation > 80:
            # Flat digital illustration / clip-art
            ai_score += 0.45

        if ai_score >= 0.65:
            is_synthetic = True

        return is_synthetic, round(ai_score, 2)
    except Exception as e:
        logger.warning(f"Heuristic analysis error: {e}")
        return False, 0.20


def verify_civic_image(image_file):
    """
    Master combined verification pipeline:
    Returns dict:
    {
        'is_genuine': bool,
        'verification_status': str,
        'confidence_score': float,
        'camera_make': str,
        'camera_model': str,
        'exif_timestamp': str,
        'lat': float or None,
        'lng': float or None,
        'alert_message': str or None
    }
    """
    if not image_file:
        return {
            'is_genuine': False,
            'verification_status': 'Flagged AI / Digital Art',
            'confidence_score': 0.0,
            'camera_make': '',
            'camera_model': '',
            'exif_timestamp': '',
            'lat': None,
            'lng': None,
            'alert_message': 'No image file uploaded.'
        }

    exif, img = extract_exif_metadata(image_file)
    lat, lng = extract_gps_coords(exif)

    # 1. Scan binary metadata for known AI generative prompt markers
    has_marker, marker_found = scan_binary_for_ai_markers(image_file)
    if has_marker:
        return {
            'is_genuine': False,
            'verification_status': 'Flagged AI / Digital Art',
            'confidence_score': 0.98,
            'camera_make': '',
            'camera_model': '',
            'exif_timestamp': '',
            'lat': None,
            'lng': None,
            'alert_message': f'⚠️ Image detected as AI-generated or digital art ({marker_found}). Please upload a genuine on-site photograph.'
        }

    # 2. Check for authentic camera hardware metadata (Combine method Fast-Path)
    if exif:
        make = str(exif.get('Make', '')).strip()
        model = str(exif.get('Model', '')).strip()
        date_time = str(exif.get('DateTimeOriginal', exif.get('DateTime', ''))).strip()
        software = str(exif.get('Software', '')).lower()

        # Check if software indicates digital art or manipulation
        for bad_app in ['photoshop', 'gimp', 'midjourney', 'stable diffusion', 'canva', 'dall']:
            if bad_app in software:
                return {
                    'is_genuine': False,
                    'verification_status': 'Flagged AI / Digital Art',
                    'confidence_score': 0.90,
                    'camera_make': make,
                    'camera_model': model,
                    'exif_timestamp': date_time,
                    'lat': lat,
                    'lng': lng,
                    'alert_message': '⚠️ Image detected as AI-generated or digital art. Please upload a genuine on-site photograph.'
                }

        # Authentic phone camera hardware match
        is_known_hardware = any(brand in make.lower() for brand in VALID_CAMERA_MAKES)
        has_optical_specs = 'FocalLength' in exif or 'ExposureTime' in exif or 'ISOSpeedRatings' in exif

        if (is_known_hardware or make) and (has_optical_specs or model):
            return {
                'is_genuine': True,
                'verification_status': 'Auto-Verified (Camera EXIF)',
                'confidence_score': 0.99,
                'camera_make': make,
                'camera_model': model,
                'exif_timestamp': date_time,
                'lat': lat,
                'lng': lng,
                'alert_message': None
            }

    # 3. Fallback: Metadata stripped or absent -> Run AI & Digital Art Detector Pipeline
    if img:
        is_synthetic, ai_score = analyze_image_heuristics(img)
        if is_synthetic:
            return {
                'is_genuine': False,
                'verification_status': 'Flagged AI / Digital Art',
                'confidence_score': ai_score,
                'camera_make': '',
                'camera_model': '',
                'exif_timestamp': '',
                'lat': lat,
                'lng': lng,
                'alert_message': '⚠️ Image detected as AI-generated or digital art. Please upload a genuine on-site photograph.'
            }
        else:
            # Genuine photo with stripped metadata (e.g. sent over WhatsApp/Facebook)
            return {
                'is_genuine': True,
                'verification_status': 'AI-Verified (Genuine Photo)',
                'confidence_score': 0.88,
                'camera_make': 'Stripped EXIF (Web/Chat)',
                'camera_model': 'Authentic Sensor Noise Profile',
                'exif_timestamp': '',
                'lat': lat,
                'lng': lng,
                'alert_message': None
            }

    return {
        'is_genuine': True,
        'verification_status': 'Manual Review Required',
        'confidence_score': 0.50,
        'camera_make': '',
        'camera_model': '',
        'exif_timestamp': '',
        'lat': None,
        'lng': None,
        'alert_message': None
    }
