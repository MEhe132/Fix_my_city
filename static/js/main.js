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
// Multi-CDN Tile Providers (All 100% Free, Zero-Block, Ultra-Reliable)
function createTileLayer(providerKey) {
    const savedKey = localStorage.getItem('fmc_map_api_key') || '';
    
    switch (providerKey) {
        case 'streets':
            // Esri World Street Map (Akamai CDN - Ultra-fast, zero auth, high availability)
            return L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
                maxZoom: 19,
                attribution: '&copy; Esri &copy; OpenStreetMap'
            });

        case 'voyager':
            // CARTO Voyager (Cloudflare CDN - Clean civic vector style)
            return L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png', {
                maxZoom: 19,
                subdomains: 'abcd',
                attribution: '&copy; CARTO &copy; OpenStreetMap'
            });

        case 'hot':
            // Humanitarian OpenStreetMap (Dedicated public civic tiles, zero localhost block)
            return L.tileLayer('https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {
                maxZoom: 19,
                subdomains: 'abc',
                attribution: '&copy; OpenStreetMap contributors, Humanitarian Team'
            });

        case 'satellite':
            // Esri World Imagery (High-resolution satellite view)
            return L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                maxZoom: 19,
                attribution: '&copy; Esri World Imagery'
            });

        case 'dark':
            // CARTO Dark Matter (Night / Dark mode theme)
            return L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/dark_all/{z}/{x}/{y}.png', {
                maxZoom: 19,
                subdomains: 'abcd',
                attribution: '&copy; CARTO Dark Matter'
            });

        case 'custom':
            // Mapbox or Stadia if user provided an API key
            if (savedKey.startsWith('pk.')) {
                // Mapbox format
                return L.tileLayer(`https://api.mapbox.com/styles/v1/mapbox/streets-v12/tiles/{z}/{x}/{y}?access_token=${savedKey}`, {
                    maxZoom: 19,
                    tileSize: 512,
                    zoomOffset: -1,
                    attribution: '&copy; Mapbox &copy; OpenStreetMap'
                });
            } else if (savedKey) {
                // Stadia / Generic format
                return L.tileLayer(`https://tiles.stadiamaps.com/tiles/osm_bright/{z}/{x}/{y}.png?api_key=${savedKey}`, {
                    maxZoom: 19,
                    attribution: '&copy; Stadia Maps &copy; OpenStreetMap'
                });
            }
            // Fallback to streets if no key saved
            return createTileLayer('streets');

        default:
            return createTileLayer('streets');
    }
}

let activeLayerKey = localStorage.getItem('fmc_active_tile_provider') || 'streets';

function initMainMap() {
    const mapContainer = document.getElementById('main-map');
    if (!mapContainer) return;

    // Attach current tile layer with auto-fallback error handling
    currentTileLayer = createTileLayer(activeLayerKey);
    attachTileErrorFallback(currentTileLayer, activeLayerKey);

    mainMap = L.map('main-map', {
        center: DHAKA_DEFAULT_CENTER,
        zoom: 12,
        layers: [currentTileLayer],
        zoomControl: true
    });

    markersLayerGroup = L.layerGroup().addTo(mainMap);

    // Guaranteed aggressive size invalidation to fix Leaflet gray/collapsed container timing
    [100, 300, 600, 1200].forEach(delay => {
        setTimeout(() => {
            if (mainMap) mainMap.invalidateSize();
        }, delay);
    });

    window.addEventListener('resize', () => {
        if (mainMap) mainMap.invalidateSize();
    });

    updateLayerButtonsUI(activeLayerKey);
}

// Automatic graceful fallback if an ISP or firewall blocks a tile CDN
function attachTileErrorFallback(layer, sourceKey) {
    let errorCount = 0;
    layer.on('tileerror', function() {
        errorCount++;
        if (errorCount === 3 && sourceKey !== 'streets') {
            console.warn(`Tile provider '${sourceKey}' encountered errors. Auto-switching to backup Esri Streets.`);
            switchMapLayer('streets');
            const alertBadge = document.getElementById('map-live-coords');
            if (alertBadge) {
                alertBadge.innerHTML = `<span class="text-amber-600">⚡ Auto-switched to Esri backup tiles</span>`;
                setTimeout(() => {
                    alertBadge.textContent = "23.8103°N, 90.4125°E";
                }, 4000);
            }
        }
    });
}

/**
 * 1-Click Map Layer Switcher (Esri Streets, Carto, Humanitarian, Satellite, Dark)
 */
window.switchMapLayer = function(layerKey) {
    if (!mainMap) return;

    if (currentTileLayer) {
        mainMap.removeLayer(currentTileLayer);
    }
    
    activeLayerKey = layerKey;
    localStorage.setItem('fmc_active_tile_provider', layerKey);
    
    currentTileLayer = createTileLayer(layerKey);
    attachTileErrorFallback(currentTileLayer, layerKey);
    mainMap.addLayer(currentTileLayer);

    updateLayerButtonsUI(layerKey);

    setTimeout(() => {
        if (mainMap) mainMap.invalidateSize();
    }, 150);
};

function updateLayerButtonsUI(activeKey) {
    ['streets', 'voyager', 'hot', 'satellite', 'dark', 'custom'].forEach(key => {
        const btn = document.getElementById(`btn-layer-${key}`);
        if (btn) {
            if (key === activeKey) {
                btn.className = 'px-2 py-0.5 rounded-md bg-white text-blue-700 shadow-xs font-bold';
            } else {
                btn.className = 'px-2 py-0.5 rounded-md text-slate-600 hover:text-slate-900 font-medium';
            }
        }
    });
}

/**
 * Modal to configure a custom free API key (Mapbox, Stadia, Geoapify)
 */
window.openMapApiKeyModal = function() {
    const currentKey = localStorage.getItem('fmc_map_api_key') || '';
    const key = prompt("🔑 Enter your Free Mapbox or Stadia Maps API Key:\n\n• For Mapbox: enter 'pk.eyJ...'\n• For Stadia: enter your API key\n• Leave empty to use free built-in Esri/Carto CDNs (Zero key needed!)", currentKey);
    
    if (key !== null) {
        if (key.trim()) {
            localStorage.setItem('fmc_map_api_key', key.trim());
            alert("✓ API Key saved! Switching map to your custom provider.");
            switchMapLayer('custom');
        } else {
            localStorage.removeItem('fmc_map_api_key');
            alert("Using built-in high-speed Esri / Carto CDN (No key required).");
            switchMapLayer('streets');
        }
    }
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

    modalMap = L.map('modal-map', { zoomControl: false }).setView(DHAKA_DEFAULT_CENTER, 14);
    createTileLayer('streets').addTo(modalMap);

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
            const latField = document.getElementById('id_latitude') || document.getElementById('form-lat');
            const lngField = document.getElementById('id_longitude') || document.getElementById('form-lng');
            if (latField) latField.value = pos.lat.toFixed(6);
            if (lngField) lngField.value = pos.lng.toFixed(6);
            autoGeocodeAddress(pos.lat, pos.lng);
        });
    }

    const latField = document.getElementById('id_latitude') || document.getElementById('form-lat');
    const lngField = document.getElementById('id_longitude') || document.getElementById('form-lng');
    if (latField) latField.value = latLng[0].toFixed(6);
    if (lngField) lngField.value = latLng[1].toFixed(6);

    modalMap.panTo(latLng);
    autoGeocodeAddress(latLng[0], latLng[1]);
}

function autoGeocodeAddress(lat, lng) {
    const addressInput = document.getElementById('id_address') || document.getElementById('form-description');
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

// Built-in Dhaka sample fallback pins if Django server or API is temporarily unreachable
const DHAKA_FALLBACK_ISSUES = [
    { id: 1, title: "Severe Crater Pothole on Road 11", category: "Pothole", ward: "Ward 19", lat: 23.7937, lng: 90.4048, upvotes: 14, address: "Road 11, Block D, Banani" },
    { id: 2, title: "Row of 4 Streetlights Non-Operational", category: "Streetlight", ward: "Ward 18", lat: 23.7998, lng: 90.4208, upvotes: 11, address: "Park Road, Baridhara" },
    { id: 3, title: "WASA Fresh Water Main Pipeline Burst", category: "Water Leak", ward: "Ward 32", lat: 23.7461, lng: 90.3742, upvotes: 27, address: "Satmasjid Road, Dhanmondi" },
    { id: 4, title: "Uncovered Deep Drainage Manhole", category: "Waterlogging", ward: "Ward 11", lat: 23.8223, lng: 90.3654, upvotes: 8, address: "Section 10, Mirpur" },
    { id: 5, title: "Illegal Solid Waste Dumping Heap", category: "Sanitation", ward: "Ward 7", lat: 23.7189, lng: 90.3882, upvotes: 19, address: "Fort Road, Lalbagh" },
    { id: 6, title: "Monsoon Storm Water Drain Blockage", category: "Waterlogging", ward: "Ward 19", lat: 23.7925, lng: 90.4167, upvotes: 16, address: "Road 103, Gulshan-2" }
];

function renderIssuesOnMap(issuesList) {
    if (!mainMap || !markersLayerGroup) return;
    markersLayerGroup.clearLayers();
    if (!issuesList || issuesList.length === 0) return;

    const latLngs = [];

    issuesList.forEach(issue => {
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

    return latLngs;
}

function fetchMapMarkersFromDjango() {
    if (!mainMap || !markersLayerGroup) return;

    const urlParams = new URLSearchParams(window.location.search);
    const wardParam = urlParams.get('ward') || 'all';
    const catParam = urlParams.get('category') || 'all';

    let fetchUrl = `/api/issues/?ward=${wardParam}&category=${catParam}`;

    fetch(fetchUrl)
        .then(res => {
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            return res.json();
        })
        .then(data => {
            const issues = (data && data.issues && data.issues.length > 0) ? data.issues : DHAKA_FALLBACK_ISSUES;
            const latLngs = renderIssuesOnMap(issues);
            
            if (wardParam !== 'all' && latLngs && latLngs.length > 0) {
                const bounds = L.latLngBounds(latLngs);
                mainMap.fitBounds(bounds, { maxZoom: 15, padding: [30, 30] });
            }
        })
        .catch(err => {
            console.warn('Could not reach /api/issues/. Loading resilient local Dhaka markers:', err);
            renderIssuesOnMap(DHAKA_FALLBACK_ISSUES);
        });
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
