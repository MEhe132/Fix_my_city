/**
 * Fix My City (Bangladesh Civic Infrastructure Issue Tracker)
 * Full-Stack Client-Side Controller:
 * - Leaflet.js GIS Mapping (Dhaka focus & Ward jurisdiction routing)
 * - AI-Generated Image & Camera Hardware Verification Pipeline
 * - 1-Click Social Campaign Generator & Clipboard Copy
 * - Instant AJAX Upvoting & Priority Escalation Handling
 * - Theme Switcher (Dark / Light)
 */

let mainMap = null;
let modalMap = null;
let modalMarker = null;
let markersLayerGroup = null;

// Dhaka, Bangladesh Geocenter
const DHAKA_DEFAULT_CENTER = [23.8103, 90.4125];

const CATEGORY_COLORS = {
    Pothole: '#ef4444',
    Streetlight: '#f59e0b',
    'Water Leak': '#3b82f6',
    Waterlogging: '#06b6d4',
    Sanitation: '#10b981',
    Footpath: '#8b5cf6',
    Other: '#64748b'
};

document.addEventListener('DOMContentLoaded', () => {
    initThemeManager();
    initMainMap();
    initModalMap();
    fetchMapMarkersFromDjango();
    setupPhotoPreviewAndAIVerifier();
});

// Helper for Django CSRF Token
function getCSRFToken() {
    const input = document.querySelector('[name=csrfmiddlewaretoken]');
    return input ? input.value : '';
}

/* ==========================================================================
   1. Theme Manager (Dark / Light)
   ========================================================================== */
function initThemeManager() {
    const themeBtn = document.getElementById('theme-toggle-btn');
    const sunIcon = document.getElementById('theme-icon-sun');
    const moonIcon = document.getElementById('theme-icon-moon');

    const savedTheme = localStorage.getItem('fmc_bd_theme') || 'light';
    applyTheme(savedTheme);

    if (themeBtn) {
        themeBtn.addEventListener('click', () => {
            const current = document.documentElement.getAttribute('data-theme') || 'light';
            const target = current === 'light' ? 'dark' : 'light';
            applyTheme(target);
        });
    }

    function applyTheme(theme) {
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('fmc_bd_theme', theme);

        if (theme === 'dark') {
            if (sunIcon) sunIcon.style.display = 'none';
            if (moonIcon) moonIcon.style.display = 'inline-block';
        } else {
            if (sunIcon) sunIcon.style.display = 'inline-block';
            if (moonIcon) moonIcon.style.display = 'none';
        }
    }
}

/* ==========================================================================
   2. Interactive Leaflet GIS Mapping (Dhaka, Bangladesh)
   ========================================================================== */
// Reliable High-Speed Commercial CDN Tile Providers (Zero 403 Policy Blocks)
const TILE_PROVIDERS = {
    voyager: L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        maxZoom: 19,
        subdomains: 'abcd',
        attribution: '&copy; OpenStreetMap &copy; CARTO'
    }),
    streets: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 19,
        attribution: '&copy; Esri World Street Map'
    }),
    satellite: L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
        maxZoom: 19,
        attribution: '&copy; Esri World Imagery'
    }),
    dark: L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}{r}.png', {
        maxZoom: 19,
        subdomains: 'abcd',
        attribution: '&copy; CARTO Dark Matter'
    })
};

let currentTileLayer = null;

function initMainMap() {
    const mapContainer = document.getElementById('main-map');
    if (!mapContainer) return;

    // Default to Carto Voyager (High-speed Cloudflare CDN, unrestricted)
    currentTileLayer = TILE_PROVIDERS.voyager;

    mainMap = L.map('main-map', {
        center: DHAKA_DEFAULT_CENTER,
        zoom: 12,
        layers: [currentTileLayer]
    });

    markersLayerGroup = L.layerGroup().addTo(mainMap);

    // Force Leaflet to calculate container size to prevent gray tiles
    setTimeout(() => {
        if (mainMap) mainMap.invalidateSize();
    }, 250);
}

/**
 * 1-Click Map Layer Switcher (Civic Clean, Streets, Satellite, Dark Mode)
 */
window.switchMapLayer = function(layerKey) {
    if (!mainMap || !TILE_PROVIDERS[layerKey]) return;

    if (currentTileLayer) {
        mainMap.removeLayer(currentTileLayer);
    }
    currentTileLayer = TILE_PROVIDERS[layerKey];
    mainMap.addLayer(currentTileLayer);

    // Update active button state
    ['voyager', 'streets', 'satellite', 'dark'].forEach(key => {
        const btn = document.getElementById(`btn-layer-${key}`);
        if (btn) {
            if (key === layerKey) {
                btn.className = 'px-2 py-0.5 rounded-md bg-white text-blue-700 shadow-xs font-bold';
            } else {
                btn.className = 'px-2 py-0.5 rounded-md text-slate-600 hover:text-slate-900 font-medium';
            }
        }
    });
};

let userLocationMarker = null;
let userAccuracyCircle = null;

/**
 * Requests browser location permission and flies the map to the user's current GPS location.
 */
window.locateUserOnMap = function() {
    const coordsDisplay = document.getElementById('map-live-coords');
    if (coordsDisplay) coordsDisplay.textContent = "Acquiring GPS...";

    if (!navigator.geolocation) {
        fallbackToIPLocation(coordsDisplay, false);
        return;
    }

    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            const accuracy = position.coords.accuracy;

            if (coordsDisplay) {
                coordsDisplay.textContent = `${lat.toFixed(4)}°N, ${lng.toFixed(4)}°E (±${Math.round(accuracy)}m)`;
            }

            if (mainMap) {
                if (userLocationMarker) mainMap.removeLayer(userLocationMarker);
                if (userAccuracyCircle) mainMap.removeLayer(userAccuracyCircle);

                // Show accuracy aura circle
                userAccuracyCircle = L.circle([lat, lng], {
                    radius: Math.min(accuracy, 200),
                    color: '#2563eb',
                    fillColor: '#60a5fa',
                    fillOpacity: 0.15,
                    weight: 1
                }).addTo(mainMap);

                // Live location marker with custom design
                userLocationMarker = L.circleMarker([lat, lng], {
                    radius: 8,
                    fillColor: '#2563eb',
                    color: '#ffffff',
                    weight: 3,
                    opacity: 1,
                    fillOpacity: 1
                }).addTo(mainMap).bindPopup(`
                    <div style="font-family: 'Plus Jakarta Sans', sans-serif;">
                        <b style="color: #2563eb;">📍 You are here</b><br>
                        <span style="font-size: 0.72rem; color: #64748b;">Live Device GPS: ${lat.toFixed(5)}, ${lng.toFixed(5)}</span>
                    </div>
                `).openPopup();

                mainMap.flyTo([lat, lng], 16, { duration: 1.5 });
            }
        },
        (error) => {
            // When browser GPS permission is denied or device lacks GPS chip, seamlessly fallback to IP geolocation!
            fallbackToIPLocation(coordsDisplay, false);
        },
        { enableHighAccuracy: true, timeout: 6000, maximumAge: 0 }
    );
};

window.locateUserInModal = function() {
    if (!navigator.geolocation) {
        fallbackToIPLocation(null, true);
        return;
    }
    navigator.geolocation.getCurrentPosition(
        (position) => {
            const lat = position.coords.latitude;
            const lng = position.coords.longitude;
            setModalPin(lat, lng);
        },
        (error) => {
            fallbackToIPLocation(null, true);
        },
        { enableHighAccuracy: true, timeout: 6000 }
    );
};

function fallbackToIPLocation(coordsDisplay, isModal = false) {
    if (coordsDisplay) coordsDisplay.textContent = "Locating via Network IP...";
    fetch('/api/ip-locate/')
        .then(res => res.json())
        .then(data => {
            const lat = data.lat || DHAKA_DEFAULT_CENTER[0];
            const lng = data.lng || DHAKA_DEFAULT_CENTER[1];
            const city = data.city || "Dhaka";

            if (coordsDisplay) {
                coordsDisplay.textContent = `${lat.toFixed(4)}°N, ${lng.toFixed(4)}°E (${city})`;
            }

            if (isModal) {
                setModalPin(lat, lng);
            } else if (mainMap) {
                if (userLocationMarker) mainMap.removeLayer(userLocationMarker);
                if (userAccuracyCircle) mainMap.removeLayer(userAccuracyCircle);

                userLocationMarker = L.circleMarker([lat, lng], {
                    radius: 8,
                    fillColor: '#8b5cf6',
                    color: '#ffffff',
                    weight: 3,
                    opacity: 1,
                    fillOpacity: 1
                }).addTo(mainMap).bindPopup(`
                    <div style="font-family: 'Plus Jakarta Sans', sans-serif;">
                        <b style="color: #8b5cf6;">📍 Approx. Location: ${city}</b><br>
                        <span style="font-size: 0.72rem; color: #64748b;">Estimated via Network IP.</span><br>
                        <span style="font-size: 0.68rem; color: #3b82f6;">Tip: Click 🔒 lock in address bar to enable exact GPS.</span>
                    </div>
                `).openPopup();

                mainMap.flyTo([lat, lng], 13, { duration: 1.5 });
            }
        })
        .catch(() => {
            if (coordsDisplay) coordsDisplay.textContent = "23.8103°N, 90.4125°E";
            if (isModal) setModalPin(DHAKA_DEFAULT_CENTER[0], DHAKA_DEFAULT_CENTER[1]);
        });
}

function initModalMap() {
    const mapContainer = document.getElementById('modal-map');
    if (!mapContainer) return;

    modalMap = L.map('modal-map').setView(DHAKA_DEFAULT_CENTER, 14);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        maxZoom: 19,
        attribution: '&copy; OpenStreetMap'
    }).addTo(modalMap);

    modalMap.on('click', (e) => {
        setModalPin(e.latlng.lat, e.latlng.lng);
    });
}

function setModalPin(lat, lng) {
    const latLng = [parseFloat(lat), parseFloat(lng)];
    if (modalMarker) {
        modalMarker.setLatLng(latLng);
    } else {
        modalMarker = L.marker(latLng, { draggable: true }).addTo(modalMap);
        modalMarker.on('dragend', (e) => {
            const pos = e.target.getLatLng();
            const latField = document.getElementById('id_latitude');
            const lngField = document.getElementById('id_longitude');
            if (latField) latField.value = pos.lat.toFixed(6);
            if (lngField) lngField.value = pos.lng.toFixed(6);
            autoGeocodeAddress(pos.lat, pos.lng);
        });
    }

    const latField = document.getElementById('id_latitude');
    const lngField = document.getElementById('id_longitude');
    if (latField) latField.value = latLng[0].toFixed(6);
    if (lngField) lngField.value = latLng[1].toFixed(6);

    modalMap.panTo(latLng);
    autoGeocodeAddress(latLng[0], latLng[1]);
}

function autoGeocodeAddress(lat, lng) {
    const addressInput = document.getElementById('id_address');
    if (!addressInput) return;

    fetch(`/api/reverse-geocode/?lat=${lat}&lng=${lng}`)
        .then(res => res.json())
        .then(data => {
            if (data && data.clean_address) {
                addressInput.value = data.clean_address;
            }
        })
        .catch(() => {});
}

function fetchMapMarkersFromDjango() {
    if (!mainMap || !markersLayerGroup) return;

    const urlParams = new URLSearchParams(window.location.search);
    const wardParam = urlParams.get('ward') || 'all';
    const catParam = urlParams.get('category') || 'all';

    let fetchUrl = `/api/issues/?ward=${wardParam}&category=${catParam}`;

    fetch(fetchUrl)
        .then(res => res.json())
        .then(data => {
            markersLayerGroup.clearLayers();
            if (!data.issues || data.issues.length === 0) return;

            const latLngs = [];

            data.issues.forEach(issue => {
                if (!issue.lat || !issue.lng) return;

                const color = CATEGORY_COLORS[issue.category] || CATEGORY_COLORS.Other;
                const marker = L.circleMarker([issue.lat, issue.lng], {
                    radius: 10,
                    fillColor: color,
                    color: '#ffffff',
                    weight: 2.5,
                    opacity: 1,
                    fillOpacity: 0.95
                });

                latLngs.push([issue.lat, issue.lng]);

                const popupHTML = `
                    <div style="font-family: 'Plus Jakarta Sans', sans-serif; min-width: 210px; max-width: 250px;">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
                            <span style="font-size: 0.7rem; font-weight: 800; color: ${color}; text-transform: uppercase;">${issue.category}</span>
                            <span style="font-size: 0.65rem; font-weight: 800; background: #e0f2fe; color: #0369a1; padding: 2px 6px; border-radius: 6px;">${issue.ward}</span>
                        </div>
                        <div style="font-weight: 800; font-size: 0.85rem; margin-bottom: 4px; line-height: 1.25;">
                            <a href="/issues/${issue.id}/" style="color: #0f172a; text-decoration: none;">${issue.title}</a>
                        </div>
                        <div style="font-size: 0.72rem; color: #64748b; margin-bottom: 6px;">${issue.address || ''}</div>
                        <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #f1f5f9; padding-top: 6px;">
                            <span style="font-weight: 800; font-size: 0.75rem; color: #2563eb;">🔥 ${issue.upvotes} Upvotes</span>
                            <a href="/issues/${issue.id}/" style="font-size: 0.75rem; font-weight: 700; color: #2563eb; text-decoration: none;">View Detail &rarr;</a>
                        </div>
                    </div>
                `;

                marker.bindPopup(popupHTML);
                markersLayerGroup.addLayer(marker);
            });

            // If filtered to a specific ward, fit map to ward pins
            if (wardParam !== 'all' && latLngs.length > 0) {
                const bounds = L.latLngBounds(latLngs);
                mainMap.fitBounds(bounds, { maxZoom: 15, padding: [30, 30] });
            }
        })
        .catch(err => console.error('Failed to fetch map markers:', err));
}

window.focusMap = function(lat, lng) {
    if (!lat || !lng || !mainMap) return;
    mainMap.flyTo([parseFloat(lat), parseFloat(lng)], 16, { duration: 1.2 });
    const mapCard = document.getElementById('main-map');
    if (mapCard) {
        mapCard.scrollIntoView({ behavior: 'smooth' });
    }
};

/* ==========================================================================
   3. AI-Generated Image & Camera Hardware Verification Pipeline
   ========================================================================== */
function setupPhotoPreviewAndAIVerifier() {
    const photoInput = document.getElementById('photo-file-input');
    const preview = document.getElementById('photo-preview');
    const badge = document.getElementById('ai-verification-badge');
    const badgeText = document.getElementById('ai-badge-text');
    const badgeScore = document.getElementById('ai-badge-score');
    const submitBtn = document.getElementById('submit-report-btn');

    if (!photoInput) return;

    photoInput.addEventListener('change', (e) => {
        const file = e.target.files[0];
        if (!file) return;

        // Visual Preview
        const reader = new FileReader();
        reader.onload = ev => {
            preview.src = ev.target.result;
            preview.classList.remove('hidden');
        };
        reader.readAsDataURL(file);

        // Send file to live backend AI & EXIF verification API
        const formData = new FormData();
        formData.append('photo', file);

        badge.classList.remove('hidden');
        badge.className = 'text-xs p-3 rounded-xl font-bold flex items-center justify-between bg-blue-50 text-blue-800 border border-blue-200';
        badgeText.textContent = 'Analyzing image metadata & synthetic art signatures...';
        badgeScore.textContent = 'SCANNING';

        fetch('/api/verify-image/', {
            method: 'POST',
            headers: { 'X-CSRFToken': getCSRFToken() },
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.success) {
                // Instantly Approved (Authentic Hardware or Optical Sensor)
                if (data.verification_status.includes('Auto-Verified')) {
                    badge.className = 'text-xs p-3 rounded-xl font-bold flex items-center justify-between bg-emerald-50 text-emerald-800 border border-emerald-300';
                    badgeText.innerHTML = `✅ Authentic Phone Camera Hardware Verified: <b>${data.camera_make} ${data.camera_model}</b>`;
                    badgeScore.textContent = '99% AUTHENTIC';
                } else {
                    badge.className = 'text-xs p-3 rounded-xl font-bold flex items-center justify-between bg-blue-50 text-blue-800 border border-blue-300';
                    badgeText.innerHTML = `🔍 Passed AI Synthetic Screening (Authentic Optical Sensor Profile)`;
                    badgeScore.textContent = 'VERIFIED GENUINE';
                }

                // Auto-set GPS pin if coordinates found in photo EXIF
                if (data.lat && data.lng) {
                    setModalPin(data.lat, data.lng);
                    badgeText.innerHTML += ` • 📍 GPS Extracted: ${data.lat}, ${data.lng}`;
                }

                if (submitBtn) {
                    submitBtn.disabled = false;
                    submitBtn.classList.remove('opacity-50', 'cursor-not-allowed');
                }
            } else {
                // Flagged AI-Generated Image or Digital Art -> Alert User & Block
                badge.className = 'text-xs p-3 rounded-xl font-bold flex items-center justify-between bg-rose-50 text-rose-800 border border-rose-300';
                badgeText.innerHTML = data.alert_message || '⚠️ Image detected as AI-generated or digital art. Please upload a genuine on-site photograph.';
                badgeScore.textContent = 'FLAGGED AI / ART';

                if (submitBtn) {
                    submitBtn.disabled = true;
                    submitBtn.classList.add('opacity-50', 'cursor-not-allowed');
                }
            }
        })
        .catch(err => {
            console.error('Image verification failed:', err);
            badge.className = 'text-xs p-3 rounded-xl font-bold flex items-center justify-between bg-amber-50 text-amber-800 border border-amber-200';
            badgeText.textContent = 'Ready for upload (Manual verification on submission).';
            badgeScore.textContent = 'STANDARD';
        });
    });
}

/* ==========================================================================
   4. Report Modal Handlers
   ========================================================================== */
window.openReportModal = function() {
    const modal = document.getElementById('report-modal');
    if (!modal) return;
    modal.classList.remove('hidden');

    setTimeout(() => {
        if (modalMap) {
            modalMap.invalidateSize();
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    pos => setModalPin(pos.coords.latitude, pos.coords.longitude),
                    () => setModalPin(DHAKA_DEFAULT_CENTER[0], DHAKA_DEFAULT_CENTER[1])
                );
            } else {
                setModalPin(DHAKA_DEFAULT_CENTER[0], DHAKA_DEFAULT_CENTER[1]);
            }
        }
    }, 200);
};

window.closeReportModal = function() {
    const modal = document.getElementById('report-modal');
    if (modal) modal.classList.add('hidden');
};

/* ==========================================================================
   5. 1-Click Social Campaign Modal (Facebook / WhatsApp)
   ========================================================================== */
window.openCampaignModal = function(issueId) {
    const modal = document.getElementById('campaign-modal');
    const textArea = document.getElementById('campaign-text-area');
    const waBtn = document.getElementById('btn-share-whatsapp');
    const fbBtn = document.getElementById('btn-share-facebook');
    const copyStatus = document.getElementById('copy-status');

    if (!modal) return;

    if (copyStatus) copyStatus.classList.add('hidden');
    textArea.value = 'Generating civic campaign post for Facebook & WhatsApp...';

    modal.classList.remove('hidden');

    fetch(`/issues/${issueId}/campaign/`)
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                const c = data.campaign;
                textArea.value = c.full_text;
                if (waBtn) waBtn.href = c.whatsapp_url;
                if (fbBtn) fbBtn.href = c.facebook_url;
            }
        })
        .catch(err => {
            console.error('Campaign error:', err);
            textArea.value = 'Failed to generate campaign. Please try again.';
        });
};

window.closeCampaignModal = function() {
    const modal = document.getElementById('campaign-modal');
    if (modal) modal.classList.add('hidden');
};

window.copyCampaignText = function() {
    const textArea = document.getElementById('campaign-text-area');
    const copyStatus = document.getElementById('copy-status');
    if (!textArea) return;

    navigator.clipboard.writeText(textArea.value).then(() => {
        if (copyStatus) copyStatus.classList.remove('hidden');
        setTimeout(() => {
            if (copyStatus) copyStatus.classList.add('hidden');
        }, 3000);
    });
};

/* ==========================================================================
   6. AJAX Upvote with Threshold Escalation Check
   ========================================================================== */
window.handleUpvote = function(issueId, btnElement) {
    fetch(`/api/upvote/${issueId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json'
        }
    })
    .then(res => res.json())
    .then(data => {
        if (data.status === 'success') {
            const textSpan = btnElement.querySelector('.upvote-text');
            if (textSpan) textSpan.textContent = `${data.upvotes} Upvotes`;
            btnElement.classList.add('bg-blue-600', 'text-white');
            fetchMapMarkersFromDjango();

            if (data.threshold_notified) {
                // Reload to reflect priority escalation banner
                location.reload();
            }
        } else if (data.status === 'already_voted') {
            alert(data.message);
        }
    })
    .catch(err => console.error('Upvote error:', err));
};
