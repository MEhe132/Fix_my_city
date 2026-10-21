# Project Proposal: Fix My City (Local Civic Issue Tracker)

## 1. Introduction

The purpose of this project is to bridge the gap between citizens and local government by providing an accessible platform for reporting civic infrastructure issues. Currently, citizens often encounter broken infrastructure such as potholes, malfunctioning streetlights, and graffiti, but the process to report these issues is typically cumbersome, opaque, and outdated. To solve this problem, we propose "Fix My City," a user-friendly web application where citizens can quickly report issues by snapping a photo, which the system will use to automatically extract GPS coordinates and plot the issue on a public, interactive map. The remainder of this proposal will detail the motivation behind this project, outline the specific technical environment and implementation challenges, describe the expected deliverables and timeline, and conclude with a summary of the project's goals.

## 2. Motivation

The problem of unreported and unresolved civic issues stems from a historical disconnect between municipal maintenance departments and the citizens who navigate the city daily. Traditional reporting methods—such as phone calls, emails, or complex municipal portals—create high friction for the user, leading to under-reporting. This problem deserves attention because well-maintained infrastructure is critical for public safety, civic pride, and efficient city functioning. These issues occur daily across all neighborhoods, often persisting for weeks or months simply because the right authorities are unaware of their exact location or severity. 

While some cities have dedicated apps or hotlines, they are often plagued by poor user interfaces, lack of transparency regarding the status of the report, and a failure to build a sense of community involvement. "Fix My City" will be more successful because it lowers the barrier to entry (simply taking a photo) and introduces a community-driven upvoting system. This transparency ensures that citizens can see what has already been reported and rally behind issues that affect them most. By automating the reporting process to the local council once an issue reaches a certain threshold of upvotes, we improve upon current solutions by ensuring that community priorities are directly communicated to decision-makers. Ultimately, this project will empower citizens, bring transparency to local government processes, and facilitate faster repair of public infrastructure.

## 3. Project Details

### Environment

The project will be developed as a web application utilizing a robust modern technology stack. The backend will be built using Python and the Django framework, chosen for its rapid development capabilities and secure architecture. For image processing and metadata extraction, the Python Imaging Library (Pillow) will be utilized to extract EXIF data, specifically the GPS coordinates embedded in photos taken by users' smartphones. The frontend mapping interface will be powered by Leaflet.js, a lightweight and open-source JavaScript library for mobile-friendly interactive maps, ensuring that users can easily view and interact with reported issues geographically. 

Hardware requirements for development are standard personal computers, while the deployment environment will require a cloud hosting provider (such as Heroku, AWS, or DigitalOcean) capable of running Python web servers and a relational database (like PostgreSQL). Software tools will include Git for version control, a local development environment, and integration with an SMTP service (such as SendGrid) to handle the automated dispatch of emails and reports to local city council contacts. 

### Issues and Challenges for Implementation

One of the primary challenges we anticipate is handling image uploads and reliably extracting GPS data. Not all users will have location services enabled on their cameras, which means the EXIF data might be missing from some photos. To address this, the application must gracefully handle missing GPS data by allowing users to manually drop a pin on the map if the automatic extraction fails. Additionally, scaling the map to handle potentially thousands of reported issues without degrading performance will require careful consideration of data clustering and efficient database queries.

We are extending existing tools like Leaflet.js and Django by combining them into a specialized civic engagement pipeline. While there are generic issue trackers, what makes this project special is the automated threshold-based reporting system. Rather than spamming the local council with an email for every single pothole reported, the system intelligently aggregates community sentiment through upvotes, only alerting authorities when an issue has been validated and prioritized by the community. 

### Deliverables

The primary deliverable will be a fully functional, responsive web application accessible via modern web browsers on both desktop and mobile devices. Conclusive evidence of the project's success will be a live demonstration where a user can upload a photo, have the location mapped automatically, and simulate the automated email generation process. 

The deliverables are structured into several key components:
1.  **User Interface & Mapping:** A responsive frontend featuring the Leaflet.js map, displaying pins for reported issues, and forms for new submissions.
2.  **Backend Processing:** A Django backend handling secure image uploads, EXIF data extraction via Pillow, and database management for issues and user upvotes.
3.  **Notification System:** An integrated automated email service that generates formal reports to designated authorities based on upvote thresholds. 

Key features of the final product will include user authentication, geolocation extraction, interactive mapping, community upvoting, and automated municipal reporting.

### Timeline

The estimated timeline for this project is [Insert Timeframe, e.g., 8 weeks]. Weeks 1-2 will focus on requirement gathering, environment setup, and basic Django architecture. Weeks 3-4 will be dedicated to implementing the image upload and EXIF data extraction features. Weeks 5-6 will cover the integration of the Leaflet.js map and the upvoting mechanics. Week 7 will involve setting up the automated email triggers and finalizing the user interface. The final week will be reserved for rigorous testing, bug fixing, and preparing the final demonstration and deployment.

## 4. Conclusion

In summary, "Fix My City" is a community-driven civic issue tracker designed to simplify the reporting of broken public infrastructure. Driven by the motivation to empower citizens and increase municipal transparency, the project addresses the friction of traditional reporting methods by using automated GPS extraction from photos and community upvoting. By leveraging Python (Django), Pillow, Leaflet.js, and SMTP integration, this web application will streamline communication between the public and local government, ultimately leading to safer and better-maintained urban environments.

## 5. References

*   Django Software Foundation. (n.d.). *Django documentation*. https://docs.djangoproject.com/
*   Clark, A. (n.d.). *Pillow (PIL Fork) Documentation*. https://pillow.readthedocs.io/
*   Agafonkin, V. (n.d.). *Leaflet - a JavaScript library for interactive maps*. https://leafletjs.com/
*   SendGrid. (n.d.). *SendGrid Documentation*. https://sendgrid.com/docs/
