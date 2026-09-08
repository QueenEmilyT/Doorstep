# Doorstep Logistics

Doorstep is a parcel delivery and logistics management system designed to support nationwide deliveries across Uganda.

The platform connects customers, Doorstep agents, and transport companies to manage parcel pickup, transportation, final delivery, tracking, payments, and agent commissions.

## Core Workflow

Customer creates a parcel  
→ Pickup agent collects the parcel  
→ Parcel is handed to a transport partner  
→ Transport partner moves the parcel to the destination  
→ Destination agent receives the parcel  
→ Final delivery is completed  
→ Delivery and commission records are updated

## Main Features

- Customer and user management
- Doorstep agent management
- Agent verification and availability
- Parcel creation and tracking
- Automatic parcel tracking numbers
- Normal and express delivery
- Transport company management
- Transport route management
- Automatic delivery fee calculation
- Pickup and final-delivery assignments
- Parcel status tracking
- Transport handover management
- Automatic tracking events
- Payment management
- Pay Before Pickup and Pay on Delivery options
- Agent commission management
- Django Admin management interface

## User Roles

The system supports four main roles:

- Customer
- Agent
- Transport Partner
- Administrator

## Parcel Journey

A parcel can move through the following stages:

1. Created
2. Awaiting Pickup
3. Picked Up
4. At Origin
5. In Transit
6. At Destination
7. Out for Delivery
8. Delivered

The system also supports cancelled parcels.

## Technology Stack

### Backend
- Python
- Django
- Django REST Framework

### Database
- PostgreSQL

### Other Technologies
- Git
- GitHub
- python-dotenv

## Project Structure

```text
backend/
├── agents/
├── config/
├── deliveries/
├── parcels/
├── payments/
├── tracking/
├── transport/
├── users/
├── manage.py
└── requirements.txt