# StudentHub: The Student Hub

## Overview

StudentHub is a centralized web platform designed to streamline and enhance the student experience at school. It aims to consolidate various aspects of student life into a single, user-friendly interface, eliminating the need to navigate multiple disparate systems.

StudentHub provides a personalized dashboard, unified course management, a campus resource navigator, smart study group formation, and an internal communication hub, all powered by intelligent algorithms to tailor the experience to each student's needs.

## Features

*   *Personalized Smart Dashboard:*
    *   Uses machine learning to provide tailored recommendations for resources, events, and study groups.
    *   Displays upcoming deadlines and important announcements.
    *   Adapts to student behavior and preferences over time.

*   *Unified Course Management:*
    *   Integrates with the school Learning Management System (LMS) or provides a fallback mechanism to access course information.
    *   Provides a consolidated view of enrolled courses, assignments, grades, and announcements.
    *   (Optional) Enables assignment submission if supported by the LMS API.

*   *Campus Resource Navigator:*
    *   Offers a comprehensive directory of campus resources (library, academic advising, career services, IT support, etc.).
    *   Includes detailed information, location, hours, contact details, and FAQs for each resource.
    *   Provides an interactive campus map with resource locations.
    *   Allows for easy searching and filtering of resources.

*   *Smart Study Group Formation:*
    *   Helps students find compatible study partners based on course enrollment, academic performance, learning styles, and preferred study times.
    *   Facilitates the creation of study group profiles.
    *   Provides a matching algorithm to suggest potential study partners or groups.
    *   Includes a built-in chat feature for group communication.

*   *Internal Communication Hub:*
    *   Provides a platform for real-time messaging between students.
    *   Supports individual and group chats.
    *   Delivers notifications for new messages, friend requests, study group invitations, and system-wide alerts.

## Technology Stack

*   *Backend:*
    *   Django (Python web framework)
    *   Django REST Framework (for building APIs)
    *   MongoDB (NoSQL database)
    *   Djongo (database connector for Django and MongoDB)
*   *Frontend:*
    *   HTML
    *   CSS
    *   Vanilla JavaScript
*   *Machine Learning:*
    *   scikit-learn (for collaborative filtering, content-based filtering, and potentially other ML tasks)
    *   pandas (for data manipulation and analysis)
    *   (Optional) Surprise (for collaborative filtering)

## API Endpoints

*   *API 1: User Data & Recommendations (/api/recommendations/)*
    *   Provides personalized recommendations for resources, events, and study groups.
*   *API 2: Course Integration (/api/courses/)*
    *   Fetches course information from the LMS or through web scraping.
*   *API 3: Resource & Service Directory (/api/resources/)*
    *   Provides access to the campus resource directory, including search and filtering.
*   *API 4: Study Group Formation (/api/studygroups/)*
    *   Manages study group profiles and provides matching functionality.
*   *API 5: Internal Communication Hub (/api/messaging/)*
    *   Handles real-time messaging and notifications.

## Getting Started

### Prerequisites

*   Python 3.7+
*   pip (Python package installer)
*   MongoDB
*   Git

### Installation

1. *Clone the repository:*

    bash
    git clone <your_github_repo_url>
    cd StudentHub
    

2. *Backend Setup:*

    *   Create a virtual environment:

        bash
        python3 -m venv venv
        

    *   Activate the virtual environment:

        *   Windows: venv\Scripts\activate
        *   macOS/Linux: source venv/bin/activate

    *   Install backend dependencies:

        bash
        pip install -r requirements.txt
        

    *   Configure the database in backend/studenthub_project/studenthub_project/settings.py.

    *   Run migrations:

        bash
        python backend/studenthub_project/manage.py migrate
        

    *   Create a superuser:

        bash
        python backend/studenthub_project/manage.py createsuperuser
        

    *   Run the development server:

        bash
        python backend/studenthub_project/manage.py runserver
        

3. *Frontend Setup:*
    *   Navigate to the frontend directory:
        bash
        cd frontend
        
    *   The frontend is built with vanilla JavaScript, HTML, and CSS, so there are no dependencies to install using a package manager like npm.

    *   Open index.html in your browser to view the frontend.
        *   If you want to start a simple server from frontend folder you can do python -m http.server

### Development

*   *Backend:* Develop backend features on the backend branch.
*   *Frontend:* Develop frontend features on the frontend branch.
    *   Write vanilla JavaScript code in .js files within the frontend directory.
    *   Structure your HTML in .html files.
    *   Style your frontend using CSS in .css files.
*   *API Endpoints:* Configure API endpoints in your frontend JavaScript code to point to the appropriate URLs on the backend server (e.g., using fetch API to make requests to the Django REST Framework APIs).
*   *CORS:* If necessary, configure CORS on the backend to allow requests from the frontend.
*   *Live Server (Optional):*  Use an extension like "Live Server" in VS Code to automatically reload HTML pages in the browser when changes are made. This can speed up development.

### Deployment

*   Deploy the backend and frontend separately to your production servers.
*   Configure environment variables for production settings (e.g., database credentials, API keys).
*   *Frontend Deployment:* Since the frontend is static (HTML, CSS, JS), you can deploy it to any web server that can serve static files (e.g., Apache, Nginx, Netlify, GitHub Pages).

## Contributing

We welcome contributions to StudentHub! If you'd like to contribute, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with clear, descriptive messages.
4. Push your branch to your forked repository.
5. Create a pull request to merge your changes into the main branch of the main repository.

## License

This project is licensed under the [MIT License](LICENSE) - see the LICENSE file for details.
