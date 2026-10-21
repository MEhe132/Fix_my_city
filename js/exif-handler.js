/**
 * Fix My City - Client-Side EXIF Metadata Parser & Geolocation Fallback
 */

class ExifHandler {
    /**
     * Extracts GPS coordinates from a File image object using Exif.js
     * @param {File} file 
     * @returns {Promise<{success: boolean, lat?: number, lng?: number, message?: string}>}
     */
    static async extractGPS(file) {
        return new Promise((resolve) => {
            if (!file || !file.type.startsWith('image/')) {
                resolve({ success: false, message: 'Invalid image file.' });
                return;
            }

            // Ensure EXIF library is loaded
            if (typeof EXIF === 'undefined') {
                resolve({ success: false, message: 'EXIF library not available.' });
                return;
            }

            try {
                EXIF.getData(file, function() {
                    const lat = EXIF.getTag(this, 'GPSLatitude');
                    const latRef = EXIF.getTag(this, 'GPSLatitudeRef');
                    const lng = EXIF.getTag(this, 'GPSLongitude');
                    const lngRef = EXIF.getTag(this, 'GPSLongitudeRef');

                    if (lat && lng && latRef && lngRef) {
                        const latDecimal = ExifHandler.convertDMSToDD(lat, latRef);
                        const lngDecimal = ExifHandler.convertDMSToDD(lng, lngRef);

                        resolve({
                            success: true,
                            lat: latDecimal,
                            lng: lngDecimal,
                            message: 'Successfully extracted GPS metadata from image EXIF data!'
                        });
                    } else {
                        resolve({
                            success: false,
                            message: 'No EXIF GPS tags found in photo (privacy stripped or disabled). Please select on map or use browser location.'
                        });
                    }
                });
            } catch (err) {
                console.warn('EXIF processing error:', err);
                resolve({ success: false, message: 'Failed to process EXIF metadata.' });
            }
        });
    }

    /**
     * Converts EXIF Degrees Minutes Seconds (DMS) array to Decimal Degrees (DD)
     */
    static convertDMSToDD(dms, ref) {
        if (!dms || dms.length < 3) return 0;

        const degrees = dms[0].numerator / dms[0].denominator || dms[0];
        const minutes = dms[1].numerator / dms[1].denominator || dms[1];
        const seconds = dms[2].numerator / dms[2].denominator || dms[2];

        let dd = degrees + (minutes / 60) + (seconds / 3600);

        if (ref === 'S' || ref === 'W') {
            dd = dd * -1;
        }

        return parseFloat(dd.toFixed(6));
    }

    /**
     * Browser HTML5 Geolocation API Fallback
     */
    static async getCurrentPosition() {
        return new Promise((resolve, reject) => {
            if (!navigator.geolocation) {
                reject(new Error('Geolocation is not supported by your browser.'));
                return;
            }

            navigator.geolocation.getCurrentPosition(
                (position) => {
                    resolve({
                        lat: position.coords.latitude,
                        lng: position.coords.longitude
                    });
                },
                (error) => {
                    reject(error);
                },
                { enableHighAccuracy: true, timeout: 8000, maximumAge: 0 }
            );
        });
    }
}

window.ExifHandler = ExifHandler;
