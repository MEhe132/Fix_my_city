# Architectural Advice: Building an API-First Backend

**Question:** Should I write the code as an API so I can easily create a mobile app later?

**Short Answer:** **YES, absolutely 100%.** This is the best industry standard practice for modern applications.

---

### The Traditional Way vs. The Modern API Way

**1. The Traditional Django Way (Monolithic):**
Normally, Django handles both the logic and the visual design. 
*   **How it works:** Django gets data from the database, merges it with an HTML template, and sends the full HTML page to the browser.
*   **The Problem:** A mobile app (like Android/iOS) doesn't know how to read HTML pages. If you build it this way, when you want to make a mobile app later, you will have to rewrite your entire backend.

**2. The Modern API-First Way (Decoupled/Headless):**
You split your project into two completely separate pieces:
*   **The Backend (Django + Django REST Framework):** Your Django code *only* talks to the database and spits out raw data in **JSON format** (this is your API). It does not care about HTML or colors.
*   **The Frontend (Web / Mobile):** You build a separate web app (using plain JavaScript, React, Vue, etc.) that asks the Django API for data and displays it on the screen.

### Why is this the Best Way?

1.  **Reusability:** Once your Django REST API is built, it can serve data to *anything*. 
    *   Your Web App can use it.
    *   Your future Android App can use it.
    *   Your future iPhone App can use it.
    *   They all talk to the exact same API. You only write the backend code once!
2.  **Team Separation:** If you work in a team, one person can write the Python/Django backend, while another person designs the User Interface, without stepping on each other's toes.
3.  **Faster Performance:** Sending raw JSON data back and forth is much faster than sending heavy HTML pages.

### How to do this in Django?

Instead of using standard Django Views that return `render(request, 'template.html')`, you should use **Django REST Framework (DRF)**. 

**Your new workflow will look like this:**
1.  **Database Models:** You define your `Issue`, `User`, `Upvote` models in Django.
2.  **Serializers:** You create DRF Serializers. A serializer's job is to take your database objects and convert them into JSON text (and vice versa).
3.  **API Views:** You create API views that return the JSON. (e.g., `GET /api/issues/` returns a list of all civic issues).
4.  **Frontend Interface:** You build your web frontend (maybe using simple HTML and Leaflet.js) and use JavaScript's `fetch()` to grab the JSON data from your Django API and plot the pins on the map.

### Summary / Recommendation
For "Fix My City", definitely build the backend as a RESTful API using **Django REST Framework**. 

Because extracting GPS from photos and showing interactive maps is complex, having a clean API that just handles the heavy lifting (saving photos, counting votes, sending emails) while your frontend handles the UI makes the project much cleaner and highly scalable for the future.
