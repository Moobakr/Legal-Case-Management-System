# Legal Case Management System

A Django-based legal case management system designed to help clients create lawsuit cases, find suitable lawyers, manage case documents, and track hearing schedules.

## Overview

This project provides a web platform for managing legal cases. Clients can sign up, log in, create new lawsuit cases, upload case documents, add case participants, and view their case dashboard.

The system also recommends lawyers and courts based on the client’s city, case type, lawyer availability, rating, experience, and consultation fee.

## Features

- Client registration and login
- Client profile management
- Create new lawsuit cases
- Choose case type:
  - Civil
  - Criminal
  - Family
  - Labor
  - Commercial
- Lawyer recommendation based on:
  - Location
  - Specialization
  - Rating
  - Experience
  - Consultation fee
- Court recommendation based on client city
- Upload case documents
- Add case participants such as:
  - Plaintiff
  - Defendant
  - Witness
  - Expert Witness
- Automatic hearing date scheduling
- Email notification after case creation
- Client dashboard with:
  - Total cases
  - Active cases
  - Upcoming hearings
- Case details page
- Django admin support

## Tech Stack

- Python
- Django
- MySQL
- HTML
- CSS
- Django Templates

## Project Structure

```text
legal-case-management-system/
├── app/
│   ├── migrations/
│   ├── templates/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   └── views.py
├── training/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── manage.py
├── Pipfile
├── Pipfile.lock
├── requirements.txt
└── README.md
