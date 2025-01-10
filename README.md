# TheFollowUp

## Overview
**TheFollowUp** is an automation tool that allows users to generate, schedule, and manage social media posts and follow-up emails with ease. By leveraging the power of OpenAI's API, TheFollowUp refines the original content and generates relevant follow-up messages. The platform supports seamless integration with email services and social media, offering a comprehensive solution for automating communication. 

The project also includes an admin panel, dynamic user management, and the ability to upgrade to a premium account to access extended features. TheFollowUp is designed with flexibility in mind, enabling users to control follow-ups at any time, and to send emails to multiple recipients simultaneously.

---

## Key Features
- **User Login and Account Management**:  
  Secure login functionality with email verification required for account creation. Users can reset passwords and access their accounts with ease.

- **Admin Panel**:  
  The project features an admin panel built with **Django**, enabling administrators to manage users, access settings, and monitor system activity.

- **Follow-up and Post Generation**:  
  Users can generate social media posts and email follow-ups using **OpenAI**'s API. The tool refines and enhances the original content, providing high-quality text for communication.

- **Email to Multiple Recipients**:  
  The platform allows users to send emails to multiple recipients simultaneously, streamlining communication processes.

- **Dynamic Follow-up Management**:  
  Users can activate or deactivate follow-ups at any time via the user-friendly dashboard.

- **Premium Account Upgrade**:  
  Users can upgrade to a premium account, allowing them to create more than 5 follow-ups. Integration with **Stripe** enables test payments for premium status.

- **Database Integration**:  
  The project uses an **SQL database** with **pgAdmin** for data storage and management.

- **Automated Email Sending**:  
  Follow-ups are automatically sent by the system using the user's connected email account (Zenbox supported, Google requires 2-step verification and app-specific password).

- **Responsive Design**:  
  The application features a responsive, collapsible sidebar menu, making it user-friendly across devices.

- **User Dashboard**:  
  A dashboard displaying all generated follow-ups, email statuses, and a preview of the created content.

---

## Tech Stack
- **Backend**: Django, Python  
- **Database**: SQL (pgAdmin)  
- **Frontend**: HTML, CSS (responsive design), JavaScript  
- **External APIs**: OpenAI API (for content generation), Stripe (for premium accounts)  
- **Email**: Zenbox (Google Mail requires 2-step verification and app password)  

---

## My Contribution
I was responsible for the majority of the project development, primarily focusing on the **backend** while also contributing to the **frontend** (HTML).

- Developed and maintained the core backend logic using **Django**.
- Integrated the OpenAI API for generating social media posts and email follow-ups.
- Designed and implemented user authentication, including email verification and password reset functionalities.
- Developed the **admin panel** for managing user accounts and follow-up statuses.
- Implemented features for premium account status, including integration with **Stripe** for payments.
- Set up the **SQL database** using **pgAdmin** to manage user and follow-up data.
- Enabled dynamic follow-up control and automated email sending.

---

## Screenshots
- **Login Screen**:  
  (Insert screenshot of the login screen here)

- **Follow-up Details**:  
  (Insert screenshot showing follow-up details and settings)

- **Dashboard**:  
  (Insert screenshot of the dashboard displaying generated emails and follow-ups)

- **Account Settings**:  
  (Insert screenshot of the account settings page)

---

## Getting Started

### Prerequisites
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
