# Parking Systems IITM
### Smart Parking Management System

A web-based parking management system built with Flask for managing parking lots and user bookings. This project demonstrates CRUD operations, user authentication, and basic admin functionality.

**Built with:**
- Python
- Flask
- Bootstrap
- SQLite

## Table of Contents
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Routes](#routes)
- [Database Schema](#database-schema)
- [Screenshots](#screenshots)

## Features

### User Features
- **User Registration & Login** - Basic signup and login forms with validation
- **Search Parking Lots** - Find parking by location or name
- **Book Parking Spots** - View available spots and make bookings
- **Release Spots** - End parking session with cost calculation
- **View Statistics** - Basic dashboard showing booking history and spending
- **Booking History** - List of past bookings

### Admin Features
- **Manage Parking Lots** - Add, edit, and delete parking lots
- **Spot Management** - Spots are created automatically when adding lots
- **View Individual Spots** - Check spot details and release if needed
- **User Overview** - See all registered users and their booking info
- **Basic Reports** - View system statistics and recent bookings
- **Search Functionality** - Filter parking lots by name or location

### Dashboard Features
- **User Dashboard** - Personal booking stats and available lots
- **User Charts Page** - Simple statistics display with Bootstrap cards
- **Admin Dashboard** - Overview of all parking lots and spots
- **Admin Reports** - Basic analytics and booking history

## Technology Stack

### Backend
- **Flask** - Python web framework
- **SQLAlchemy** - Database ORM for managing data
- **WTForms** - Form handling and validation
- **SQLite** - Local database file

### Frontend
- **HTML5 & CSS3** - Basic web structure
- **Bootstrap 5.3** - CSS framework for styling
- **Minimal JavaScript** - Bootstrap functionality only

## Routes

### Authentication
- `GET/POST /` - Login page
- `GET/POST /signup` - User registration
- `GET /logout` - Logout and clear session

### User Routes
- `GET/POST /user-dashboard` - Main user page with booking functionality
- `GET /user-charts` - User statistics page
- `POST /release-parking` - Release current parking spot

### Admin Routes
- `GET /admin-dashboard` - Admin main page
- `GET /admin/users` - List all users
- `GET /admin/reports` - System reports and statistics
- `POST /add-parking-lot` - Create new parking lot
- `GET/POST /edit-parking-lot/<id>` - Edit existing parking lot
- `POST /delete-parking-lot/<id>` - Remove parking lot
- `POST /release-spot/<id>` - Admin release any spot
- `GET /view-parking-spot/<id>` - Individual spot details
- `POST /edit-spot-name/<id>` - Change spot name/number
- `POST /change-spot-status/<id>` - Toggle spot availability

## Database Schema

### Users Table
- `id` (Primary Key)
- `email` (Unique identifier)
- `password` (Plain text - for demo purposes)
- `fullname`
- `address`
- `phone`
- `pincode`

### Parking Lots Table
- `id` (Primary Key)
- `name`
- `location`
- `total_spots`
- `available_spots`
- `price_per_hour`

### Parking Spots Table
- `id` (Primary Key)
- `spot_number` (e.g., A01, A02)
- `is_occupied` (Boolean)
- `parking_lot_id` (Foreign Key)

### Bookings Table
- `id` (Primary Key)
- `vehicle_number`
- `booking_time`
- `release_time`
- `status` (active/completed/cancelled)
- `total_cost`
- `user_id` (Foreign Key)
- `parking_spot_id` (Foreign Key)
- `parking_lot_id` (Foreign Key)

## How It Works

### Spot Management
- When you create a parking lot, spots are automatically generated (A01, A02, etc.)
- Removing lots only works if they're not currently occupied in any spot
- Each spot tracks its occupied status

### Booking Process
- Users select a parking lot from the list
- System shows available spots for that lot
- User picks a spot and enters vehicle number
- Spot becomes occupied and unavailable to others
- Cost calculated when user releases the spot

### Pricing
- Each parking lot has its own hourly rate
- Minimum charge is 1 hour
- Final cost = hourly rate × hours parked (rounded up)

### Admin Functions
- First registered user becomes admin automatically
- Admins can manage all parking lots and spots
- Can view all user information and booking history
- Can manually release any occupied spot

### Basic Statistics
- User dashboard shows total bookings and spending
- Admin reports show system-wide stats
- Simple counting and summation of database records