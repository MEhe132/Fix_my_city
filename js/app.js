/**
 * Fix My City - Application Controller & GIS Map Engine
 */

document.addEventListener('DOMContentLoaded', () => {
    // --- Application State ---
    let mainMap = null;
    let modalMap = null;
    let modalMarker = null;
    let markersLayerGroup = null;

    let currentCategory = 'all';
    let searchQuery = '';
    let currentSort = 'upvotes';

    // Track user votes in memory for current session
    const userVotedIssues = new Set();

    // Default GIS Center (New York / Standard City Center)
    const CITY_CENTER = [40.7128, -74.0060];
    const DEFAULT_ZOOM = 13;

    // --- Category Color Mapping for Leaflet Markers ---
    const CATEGORY_COLORS = {
        Pothole: '#ef4444',
        Streetlight: '#f59e0b',
        'Water Leak': '#3b82f6',
        Sanitation: '#8b5cf6',
        Graffiti: '#ec4899',
        Other: '#64748b'
    };

    // --- Initialize Application ---
    function initApp() {
        initMainMap();
        initModalMap();
        setupEventListeners();
        renderAll();
    }

    // --- Main GIS Leaflet Map Setup ---
    function initMainMap() {
        mainMap = L.map('main-map').setView(CITY_CENTER, DEFAULT_ZOOM);

        // Tile layer (CartoDB Voyager tile server for clean vector look)
        L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
            maxZoom: 19,
            attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/">CARTO</a>'
        }).addTo(mainMap);

        markersLayerGroup = L.layerGroup().addTo(mainMap);
    }

    // --- Modal Selection Mini Map Setup ---
    function initModalMap() {
        modalMap = L.map('modal-map').setView(CITY_CENTER, 14);

        L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
            maxZoom: 19,
            attribution: '&copy; OpenStreetMap'
        }).addTo(modalMap);

        // Click on modal map to drop or move pin manually
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
                document.getElementById('form-lat').value = pos.lat;
                document.getElementById('form-lng').value = pos.lng;
            });
        }

        document.getElementById('form-lat').value = lat;
        document.getElementById('form-lng').value = lng;
        modalMap.panTo(latLng);
    }

    // --- Render Pipeline ---
    function renderAll() {
        const filteredIssues = window.civicDB.filter({
            category: currentCategory,
            search: searchQuery,
            sortBy: currentSort
        });

        renderMapMarkers(filteredIssues);
        renderIssueFeed(filteredIssues);
        updateStats();
    }

    // --- Render Map Markers ---
    function renderMapMarkers(issues) {
        markersLayerGroup.clearLayers();

        issues.forEach(issue => {
            const color = CATEGORY_COLORS[issue.category] || CATEGORY_COLORS.Other;
            
            // Custom Leaflet Circle Marker
            const marker = L.circleMarker([issue.lat, issue.lng], {
                radius: 9,
                fillColor: color,
                color: '#ffffff',
                weight: 2,
                opacity: 1,
                fillOpacity: 0.9
            });

            // Map Popup content
            const popupHTML = `
                <div style="font-family: 'Inter', sans-serif; min-width: 180px;">
                    <div style="font-size: 0.75rem; font-weight: 700; color: ${color}; text-transform: uppercase;">${issue.category}</div>
                    <div style="font-weight: 700; font-size: 0.95rem; margin: 0.2rem 0;">${issue.title}</div>
                    <div style="font-size: 0.8rem; color: #4a5568; margin-bottom: 0.5rem;">${issue.address}</div>
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="font-weight: 700; font-size: 0.85rem; color: #3b82f6;">🔥 ${issue.upvotes} Upvotes</span>
                        <span style="font-size: 0.7rem; padding: 0.2rem 0.5rem; background: #e2e8f0; border-radius: 4px; font-weight: 600;">${issue.status}</span>
                    </div>
                </div>
            `;

            marker.bindPopup(popupHTML);
            markersLayerGroup.addLayer(marker);
        });
    }

    // --- Render Issue Feed Cards ---
    function renderIssueFeed(issues) {
        const container = document.getElementById('issue-feed');
        container.innerHTML = '';

        if (issues.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 3rem 1rem; color: var(--text-muted);">
                    <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-bottom: 0.5rem;">
                        <circle cx="12" cy="12" r="10"/>
                        <line x1="12" y1="8" x2="12" y2="12"/>
                        <line x1="12" y1="16" x2="12.01" y2="16"/>
                    </svg>
                    <p style="font-weight: 600;">No issues found</p>
                    <p style="font-size: 0.8rem;">Try clearing search or category filters.</p>
                </div>
            `;
            return;
        }

        issues.forEach(issue => {
            const isVoted = userVotedIssues.has(issue.id);
            const formattedDate = new Date(issue.createdAt).toLocaleDateString(undefined, {
                month: 'short',
                day: 'numeric'
            });

            let statusClass = 'badge-pending';
            if (issue.status === 'Council Notified') statusClass = 'badge-notified';
            if (issue.status === 'Scheduled for Repair' || issue.status === 'Resolved') statusClass = 'badge-resolved';

            const card = document.createElement('div');
            card.className = 'issue-card-neo';

            card.innerHTML = `
                <div class="issue-top">
                    <span class="issue-badge ${statusClass}">${issue.status}</span>
                    <span class="issue-category-tag">${issue.category}</span>
                </div>

                <div class="issue-card-title">${issue.title}</div>
                <div class="issue-card-desc">${issue.description}</div>
                
                ${issue.photo ? `<img src="${issue.photo}" class="issue-image-thumb" alt="${issue.title}">` : ''}

                ${issue.upvotes >= 10 ? `
                    <div class="threshold-banner">
                        ⚡ Priority Threshold Reached! Automated Council Email Dispatched.
                    </div>
                ` : ''}

                <div class="issue-card-footer">
                    <button class="upvote-btn-neo ${isVoted ? 'voted' : ''}" data-id="${issue.id}">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="${isVoted ? 'currentColor' : 'none'}" stroke="currentColor" stroke-width="2">
                            <path d="M12 19V5M5 12l7-7 7 7"/>
                        </svg>
                        <span>${issue.upvotes} Upvote${issue.upvotes !== 1 ? 's' : ''}</span>
                    </button>

                    <div style="display: flex; align-items: center; gap: 0.75rem;">
                        <span style="font-size: 0.75rem; color: var(--text-light);">${formattedDate}</span>
                        <button class="action-link-btn" data-lat="${issue.lat}" data-lng="${issue.lng}">View Map</button>
                    </div>
                </div>
            `;

            container.appendChild(card);
        });

        // Attach Card Action Event Handlers
        container.querySelectorAll('.upvote-btn-neo').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const issueId = btn.getAttribute('data-id');
                userVotedIssues.add(issueId);
                window.civicDB.upvoteIssue(issueId);
                renderAll();
            });
        });

        container.querySelectorAll('.action-link-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                const lat = parseFloat(btn.getAttribute('data-lat'));
                const lng = parseFloat(btn.getAttribute('data-lng'));
                mainMap.flyTo([lat, lng], 16, { duration: 1.2 });
                document.querySelector('.map-card-neo').scrollIntoView({ behavior: 'smooth' });
            });
        });
    }

    // --- Update Header Statistics ---
    function updateStats() {
        const stats = window.civicDB.getStats();
        document.getElementById('stat-total').textContent = stats.total;
        document.getElementById('stat-notified').textContent = stats.notified;
        document.getElementById('stat-resolved').textContent = stats.resolved;
    }

    // --- Setup Event Handlers ---
    function setupEventListeners() {
        // Search Input
        const searchInput = document.getElementById('search-input');
        searchInput.addEventListener('input', (e) => {
            searchQuery = e.target.value;
            renderAll();
        });

        // Category Filter Chips
        const chips = document.querySelectorAll('#category-chips .chip-neo');
        chips.forEach(chip => {
            chip.addEventListener('click', () => {
                chips.forEach(c => c.classList.remove('active'));
                chip.classList.add('active');
                currentCategory = chip.getAttribute('data-category');
                renderAll();
            });
        });

        // Sort Selection
        const sortSelect = document.getElementById('sort-select');
        sortSelect.addEventListener('change', (e) => {
            currentSort = e.target.value;
            renderAll();
        });

        // Modal Controls
        const modal = document.getElementById('report-modal');
        const openModalBtn = document.getElementById('open-report-btn');
        const closeModalBtn = document.getElementById('close-modal-btn');
        const reportForm = document.getElementById('report-form');

        openModalBtn.addEventListener('click', () => {
            modal.classList.remove('hidden');
            setTimeout(() => {
                modalMap.invalidateSize();
                
                // Fallback attempt to get user HTML5 geolocation
                if (navigator.geolocation) {
                    navigator.geolocation.getCurrentPosition(
                        (pos) => setModalPin(pos.coords.latitude, pos.coords.longitude),
                        () => setModalPin(CITY_CENTER[0], CITY_CENTER[1])
                    );
                } else {
                    setModalPin(CITY_CENTER[0], CITY_CENTER[1]);
                }
            }, 250);
        });

        closeModalBtn.addEventListener('click', () => {
            modal.classList.add('hidden');
            reportForm.reset();
            resetPhotoUpload();
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.add('hidden');
                reportForm.reset();
                resetPhotoUpload();
            }
        });

        // Photo Upload & EXIF GPS Extraction
        const dropzone = document.getElementById('photo-dropzone');
        const fileInput = document.getElementById('form-photo-file');
        const photoPreview = document.getElementById('photo-preview');
        const exifFeedback = document.getElementById('exif-feedback');

        dropzone.addEventListener('click', () => fileInput.click());

        fileInput.addEventListener('change', async (e) => {
            const file = e.target.files[0];
            if (!file) return;

            // Generate thumbnail data URL
            const reader = new FileReader();
            reader.onload = (event) => {
                photoPreview.src = event.target.result;
                photoPreview.style.display = 'block';
            };
            reader.readAsDataURL(file);

            // Extract EXIF Metadata
            const exifResult = await window.ExifHandler.extractGPS(file);
            exifFeedback.style.display = 'inline-flex';

            if (exifResult.success && exifResult.lat && exifResult.lng) {
                exifFeedback.className = 'exif-status-badge exif-success';
                exifFeedback.innerHTML = `📍 GPS EXIF Found: ${exifResult.lat}, ${exifResult.lng}`;
                setModalPin(exifResult.lat, exifResult.lng);
            } else {
                exifFeedback.className = 'exif-status-badge exif-info';
                exifFeedback.innerHTML = `ℹ️ ${exifResult.message || 'No GPS metadata in photo.'}`;
            }
        });

        function resetPhotoUpload() {
            photoPreview.style.display = 'none';
            photoPreview.src = '';
            exifFeedback.style.display = 'none';
        }

        // Form Submit Handler
        reportForm.addEventListener('submit', (e) => {
            e.preventDefault();

            const lat = parseFloat(document.getElementById('form-lat').value);
            const lng = parseFloat(document.getElementById('form-lng').value);

            if (isNaN(lat) || isNaN(lng)) {
                alert('Please select a valid location by clicking on the mini-map!');
                return;
            }

            const newIssueData = {
                title: document.getElementById('form-title').value,
                category: document.getElementById('form-category').value,
                severity: document.getElementById('form-severity').value,
                description: document.getElementById('form-description').value,
                lat: lat,
                lng: lng,
                photo: photoPreview.src || null
            };

            const createdIssue = window.civicDB.addIssue(newIssueData);
            
            // Mark user as having upvoted their own report
            userVotedIssues.add(createdIssue.id);

            // Reset and close modal
            modal.classList.add('hidden');
            reportForm.reset();
            resetPhotoUpload();

            // Re-render and navigate to new issue on map
            renderAll();
            mainMap.flyTo([createdIssue.lat, createdIssue.lng], 16, { duration: 1.5 });
        });
    }

    // Launch Application
    initApp();
});
