# Strategic Plan & Critical Recommendations (Fix My City)

*This document contains critical strategic advice and technical recommendations to ensure "Fix My City" is actually successful in a real-world scenario in Bangladesh.*

## 1. The Core Strategy Shift (Escalation over Email)
Relying solely on automated emails (SMTP) to local councils will not work in Bangladesh because government emails are often unmonitored or block automated mail. Instead, the platform must use a **3-Layer Escalation System**:

*   **Layer 1: Public Visibility (0 - 10 Upvotes)**
    *   Action: Issue is posted on the public map.
    *   Feature: Generate a shareable link (e.g., `fixmycity.bd/issue/1234`) with a social share button to post directly to Facebook.
    *   Goal: Create visible community pressure.
*   **Layer 2: Social & Official Alert (10 - 50 Upvotes)**
    *   Action: Once the threshold is met, the system prompts users to share an auto-generated post tagging the local Ward Councillor on Facebook.
    *   Feature: Integration with social media sharing.
*   **Layer 3: Formal Escalation (50+ Upvotes or 14 Days Unresolved)**
    *   Action: The system automatically generates a formal **Right to Information (RTI) Act 2009** application PDF.
    *   Feature: Auto-fill RTI template generator. The system also suggests calling the national `333` helpline with the issue details.

## 2. Technical Stack Additions (To-Do List)
To support the strategy above, the following features MUST be built into the Django backend:

*   [ ] **GeoDjango + PostGIS:** Essential for determining *which* ward an issue is in (Jurisdiction Routing). Without this, we can't notify the correct Ward Councillor.
*   [ ] **Facebook OAuth Login:** Most users will not create a new email/password account. Facebook login is mandatory for quick adoption.
*   [ ] **Bangla Language Support (i18n):** The interface must support Bangla fully (or be Bangla-first).
*   [ ] **SMS Gateway Integration:** Instead of just SendGrid (Email), we must integrate a local SMS gateway (like Bulk SMS BD) to notify users of status updates, as SMS is much more reliable than email in BD.
*   [ ] **SEO-Indexable Public Pages:** Each reported issue needs its own dedicated, public web page so it can be indexed by Google and shared easily by journalists or local news pages.

## 3. The "Cold Start" Plan (Launch Strategy)
An empty map won't attract users. To launch successfully:
1.  Target **ONE single ward** first (do not launch city-wide).
2.  Manually walk the ward and report 20-30 real issues to populate the map.
3.  Share the populated map to local ward Facebook groups, tagging the specific councillor. 

## 4. Updates Needed for the Project Proposal
The academic proposal needs to be updated. Section 3 ("Issues and Challenges") must be expanded to include:
*   **Municipal Integration Risks:** The challenge of getting government officials to actually look at a 3rd party dashboard.
*   **Jurisdiction Routing:** The technical challenge of mapping a GPS coordinate to a specific administrative ward.
*   **Moderation & Spam:** Preventing duplicate reports for the same pothole, and filtering out fake reports.
*   **Language Barrier:** Designing an interface simple enough for non-English speakers.
