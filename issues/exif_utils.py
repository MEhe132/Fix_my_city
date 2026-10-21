from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import logging

logger = logging.getLogger(__name__)

def get_exif_data(image_file):
    """
    Extract raw EXIF dictionary from an uploaded image file using Pillow.
    """
    try:
        image = Image.open(image_file)
        exif = image._getexif()
        if not exif:
            return None

        exif_data = {}
        for tag, value in exif.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = value[t]
                exif_data['GPSInfo'] = gps_data
            else:
                exif_data[decoded] = value
        return exif_data
    except Exception as e:
        logger.warning(f"Error reading EXIF data with Pillow: {e}")
        return None

def convert_to_degrees(value):
    """
    Helper to convert EXIF DMS (Degrees, Minutes, Seconds) tuple to float degrees.
    """
    try:
        d = float(value[0])
        m = float(value[1])
        s = float(value[2])
        return d + (m / 60.0) + (s / 3600.0)
    except Exception:
        return 0.0

def extract_lat_lng_from_exif(image_file):
    """
    Extract Decimal Latitude and Longitude from uploaded photo EXIF metadata using Pillow.
    """
    exif = get_exif_data(image_file)
    if not exif or 'GPSInfo' not in exif:
        return None, None

    gps_info = exif['GPSInfo']
    gps_latitude = gps_info.get('GPSLatitude')
    gps_latitude_ref = gps_info.get('GPSLatitudeRef')
    gps_longitude = gps_info.get('GPSLongitude')
    gps_longitude_ref = gps_info.get('GPSLongitudeRef')

    if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
        lat = convert_to_degrees(gps_latitude)
        if gps_latitude_ref != 'N':
            lat = -lat

        lng = convert_to_degrees(gps_longitude)
        if gps_longitude_ref != 'E':
            lng = -lng

        return round(lat, 6), round(lng, 6)

    return None, None
