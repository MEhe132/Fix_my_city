# Requirement Analysis Report: Fix My City

## 1. Introduction
### 1.1 Purpose
The purpose of this document is to define the software requirements for "Fix My City," a web application designed to bridge the gap between citizens and local government. It allows users to report civic infrastructure issues (e.g., potholes, broken streetlights) by uploading photos, which are automatically mapped and reported to local authorities upon reaching a community support threshold.

### 1.2 Scope
The system will provide a user-friendly mobile and desktop web interface. It will utilize image metadata (EXIF) and HTML5 Geolocation to plot issues on an interactive map. Core features include issue submission, community upvoting, automated threshold-based email reporting, and an administrative dashboard for local councils.

## 2. Overall Description
### 2.1 User Classes and Characteristics
*   **Citizens (Standard Users):** General public who encounter civic issues. They require a simple, low-friction interface (preferably mobile-friendly) to report and view issues.
*   **Council Representatives (Admins):** Government officials who receive reports and update the status of issues (e.g., "Under Review", "Resolved"). They require a dashboard view.

### 2.2 Operating Environment
*   **Client-Side:** Modern web browsers on mobile (iOS/Android) and desktop environments.
*   **Server-Side:** Python web server (e.g., Gunicorn/WSGI) running on a cloud provider (e.g., Heroku, AWS).
*   **Database:** PostgreSQL with PostGIS extensions for spatial data.

## 3. Functional Requirements

### 3.1 Issue Reporting
*   **FR-1.1:** The system shall allow users to upload photos of civic issues.
*   **FR-1.2:** The system shall extract GPS coordinates from the uploaded image's EXIF data.
*   **FR-1.3:** If EXIF data is missing, the system shall prompt the user to use device geolocation (HTML5) or manually drop a pin on the map.
*   **FR-1.4:** Users must provide a brief description and select a category (e.g., Road, Lighting, Sanitation) for the issue.

### 3.2 Mapping and Visualization
*   **FR-2.1:** The system shall display an interactive map (using Leaflet.js) showing all reported and unresolved issues.
*   **FR-2.2:** The map shall support clustering to ensure performance when thousands of pins are present.

### 3.3 Community Upvoting
*   **FR-3.1:** Authenticated users shall be able to view and "upvote" issues reported by others.
*   **FR-3.2:** The system shall prevent a single user from upvoting the same issue multiple times.

### 3.4 Automated Notification System
*   **FR-4.1:** The system shall monitor the upvote count of every issue.
*   **FR-4.2:** Once an issue surpasses a pre-defined threshold of upvotes, the system shall automatically generate and send an email report (via SMTP/SendGrid) to the relevant local authority.

### 3.5 Council Dashboard (Moderation & Status)
*   **FR-5.1:** The system shall provide a secure login for council administrators.
*   **FR-5.2:** Administrators shall be able to update the status of an issue (e.g., Pending, Scheduled, Resolved).
*   **FR-5.3:** Administrators shall be able to moderate/remove inappropriate submissions.

## 4. Non-Functional Requirements

### 4.1 Performance
*   The interactive map should load and render issue pins within 3 seconds on a standard 4G/LTE mobile connection.

### 4.2 Security and Privacy
*   **Privacy:** The system shall strip EXIF metadata from images before serving them publicly to protect user privacy.
*   **Security:** Standard web security measures (CSRF tokens, SQL injection prevention) provided by Django must be enforced. User passwords must be hashed.

### 4.3 Reliability and Availability
*   The system should utilize robust cloud hosting to ensure 99% uptime, as civic issues can occur at any time.

## 5. Technology Stack Summary
*   **Backend Framework:** Python / Django (GeoDjango)
*   **Database:** PostgreSQL + PostGIS (for spatial queries and jurisdiction routing)
*   **Frontend UI:** HTML/CSS/JS, responsive design principles
*   **Map Interface:** Leaflet.js
*   **Image Processing:** Pillow (Python Imaging Library)
*   **Email Delivery:** SendGrid (or similar SMTP service)
