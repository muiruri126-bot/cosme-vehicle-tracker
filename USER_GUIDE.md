# Vehicle Request Tracker — User Guide

**Plan International Kenya**
Version 1.0 | February 2026

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [User Roles & Permissions](#2-user-roles--permissions)
3. [Registration & Login](#3-registration--login)
4. [Dashboard](#4-dashboard)
5. [Vehicle Bookings](#5-vehicle-bookings)
6. [Trips](#6-trips)
7. [Vehicles](#7-vehicles)
8. [Maintenance](#8-maintenance)
9. [Reports](#9-reports)
10. [Calendar](#10-calendar)
11. [User Management (Admin)](#11-user-management-admin)
12. [Audit Log (Admin)](#12-audit-log-admin)
13. [Profile & Password Management](#13-profile--password-management)
14. [Validation Rules Reference](#14-validation-rules-reference)
15. [Email Notifications](#15-email-notifications)
16. [Security Features](#16-security-features)
17. [Troubleshooting & FAQs](#17-troubleshooting--faqs)

---

## 1. Getting Started

The **Vehicle Request Tracker** is an internal web application for tracking vehicle bookings, trips, maintenance, and avoiding scheduling conflicts.

### Accessing the System
- Open the application URL in your web browser (Chrome, Edge, Firefox, or Safari recommended).
- You will be directed to the **Login** page.

### Default Admin Account
On first launch, a default administrator account is created:
- **Username:** `admin`
- **Password:** `admin123`
- You will be required to change this password on first login.

---

## 2. User Roles & Permissions

The system has three user roles:

| Feature | Admin | Driver | Requester |
|---|:---:|:---:|:---:|
| View Dashboard, Bookings, Calendar, Reports | ✔ | ✔ | ✔ |
| Create a Booking | ✔ | ✔ | ✔ |
| Cancel a Booking (Pending/Approved) | ✔ | ✔ | ✔ |
| Start / End a Trip | ✔ | ✔ | ✔ |
| Approve Bookings | ✔ | ✗ | ✗ |
| Assign a Driver to a Booking | ✔ | ✗ | ✗ |
| Add / Edit / Delete Vehicles | ✔ | ✗ | ✗ |
| Add / Complete / Cancel / Delete Maintenance | ✔ | ✗ | ✗ |
| Manage Users (List, Edit, Delete, Reset Password) | ✔ | ✗ | ✗ |
| View Audit Log | ✔ | ✗ | ✗ |
| Edit Own Profile / Change Password | ✔ | ✔ | ✔ |

> **Note:** All new registrations default to the **Requester** role. An admin can change a user's role later.

---

## 3. Registration & Login

### 3.1 Registering a New Account

1. Click **"Register here"** on the login page.
2. Fill in the required fields:

| Field | Requirement |
|---|---|
| Full Name | Required |
| Username | Required, minimum 3 characters, letters/numbers/dots/underscores only |
| Email | Required, must be a valid email address |
| Password | Required, minimum 6 characters |
| Confirm Password | Must match the password above |

3. Click **Register**. You will be redirected to the login page.

#### ✅ Validation Checks
- Username must be unique (not already taken).
- Email must be unique (not already registered).
- Username allows only: `a-z`, `A-Z`, `0-9`, `.`, `_`
- Passwords must be at least 6 characters and must match.

### 3.2 Logging In

1. Enter your **Username** and **Password**.
2. Click **Login**.

#### ✅ Validation Checks
- Both fields are required.
- Deactivated accounts cannot log in (contact your admin).
- Login is rate-limited to **10 attempts per minute** for security.

### 3.3 Forgot Password

1. Click **"Forgot your password?"** on the login page.
2. Enter your registered email address.
3. A password reset link will be sent to your email (valid for **24 hours**).
4. Click the link, then set your new password (minimum 6 characters).

#### ✅ Validation Checks
- Rate-limited to 5 requests per minute.
- Reset tokens expire after 24 hours.
- New password must be at least 6 characters.

---

## 4. Dashboard

After logging in, you will see the **Dashboard** with summary statistics:

- **Total Vehicles** in the system
- **Active Bookings** (pending + approved)
- **Total Trips** completed
- **Upcoming Maintenance** records

The dashboard provides a quick overview of the system's current state.

---

## 5. Vehicle Bookings

### 5.1 Viewing Bookings

- Navigate to **Bookings** from the navbar.
- Bookings are displayed in a paginated table (20 per page).
- Use the **Status filter** to view bookings by status: Pending, Approved, Completed, or Cancelled.

### 5.2 Creating a New Booking

1. Click **"New Booking"**.
2. Fill in the booking form:

| Field | Required | Validation |
|---|:---:|---|
| Vehicle | Yes | Must select a vehicle; vehicles under maintenance are disabled |
| Assigned Driver | No | Optional; select from available drivers |
| Planned Start Date/Time | Yes | Cannot be in the past |
| Planned End Date/Time | Yes | Must be after the start date/time |
| Route From | Yes | Text field |
| Route To | Yes | Text field |
| Purpose | Yes | Text area describing trip purpose |
| Activity Code | No | Optional reference code |
| Project Code | No | Optional project reference for budget tracking |

3. Click **Submit**.

#### ✅ Validation Checks
- **Schedule Conflict Detection:** The system checks if the selected vehicle already has a pending or approved booking that overlaps with the requested time range. If a conflict exists, the booking is rejected.
- **Conflict Formula:** Two bookings overlap when `Booking A start < Booking B end` AND `Booking B start < Booking A end`.
- **Past Date Check:** Start date/time cannot be in the past.
- **Duration Check:** End date/time must be after start date/time.
- **Vehicle Availability:** Vehicles with status "Maintenance" cannot be booked.

### 5.3 Booking Status Flow

```
Pending → Approved → Trip Started → Trip Ended → Completed
   ↓          ↓
Cancelled  Cancelled
```

### 5.4 Approving a Booking (Admin Only)

1. Open a booking with **Pending** status.
2. Click **Approve**.

#### ✅ Validation Checks
- Only **Pending** bookings can be approved.
- The system re-checks for scheduling conflicts at the time of approval.

### 5.5 Cancelling a Booking

1. Open the booking.
2. Click **Cancel**.

#### ✅ Validation Checks
- Only **Pending** or **Approved** bookings can be cancelled.

### 5.6 Assigning a Driver (Admin Only)

1. Open the booking detail page.
2. Under **"Assign / Change Driver"**, select a driver from the dropdown.
3. Click **Assign**.

### 5.7 Deleting a Booking (Admin Only)

- Click the **Delete** button on the booking detail page or the booking list.
- This also deletes any associated trip data.
- **This action cannot be undone.**

---

## 6. Trips

### 6.1 Starting a Trip

1. Open an **Approved** booking.
2. Click **Start Trip**.
3. Fill in:

| Field | Required | Validation |
|---|:---:|---|
| Actual Start Date/Time | Yes | Valid date/time |
| Odometer Start (km) | Yes | Must be a non-negative integer |

4. Click **Start Trip**.

#### ✅ Validation Checks
- Only **Approved** bookings without an existing trip can start a trip.
- Odometer reading must be 0 or greater.
- Starting a trip sets the vehicle status to **In Use**.

### 6.2 Ending a Trip

1. Open the booking with an active trip.
2. Click **End Trip**.
3. Fill in:

| Field | Required | Validation |
|---|:---:|---|
| Actual End Date/Time | Yes | Must be after the trip start time |
| Odometer End (km) | Yes | Must be ≥ Odometer Start reading |
| Fuel Used (Litres) | No | Must be non-negative if provided |
| Fuel Cost (KES) | No | Must be non-negative if provided |
| Remarks | No | Free text |

4. Click **End Trip**.

#### ✅ Validation Checks
- End date/time must be **after** the start date/time.
- Odometer End must be **≥ Odometer Start** (you can't drive negative distance).
- Fuel Used and Fuel Cost must be non-negative numbers (if provided).
- Distance is **automatically calculated** as: `Odometer End − Odometer Start`.
- Ending a trip sets the booking status to **Completed** and vehicle status back to **Available**.

---

## 7. Vehicles

### 7.1 Viewing Vehicles

- Navigate to **Vehicles** from the navbar.
- All authenticated users can view the vehicle list.

### 7.2 Adding a Vehicle (Admin Only)

1. Click **"Add Vehicle"**.
2. Fill in:

| Field | Required | Validation |
|---|:---:|---|
| Registration Number | Yes | Minimum 3 characters, must be unique |
| Make | Yes | e.g., Toyota, Nissan |
| Model | Yes | e.g., Land Cruiser, Patrol |
| Status | — | Available (default) or Maintenance |

3. Click **Add Vehicle**.

#### ✅ Validation Checks
- Registration number is **automatically converted to uppercase**.
- Registration number must be **unique** across all vehicles.
- All three fields (Registration, Make, Model) are required.

### 7.3 Editing a Vehicle (Admin Only)

1. Click **Edit** on the vehicle list.
2. Update the desired fields.
3. Click **Update Vehicle**.

#### ✅ Validation Checks
- Same as adding, plus uniqueness check excludes the current vehicle.

### 7.4 Deleting a Vehicle (Admin Only)

- Click **Delete** on a vehicle.
- **Warning:** This deletes ALL associated maintenance records, bookings, and trip data.
- **This action cannot be undone.**

### Vehicle Status Flow

| Status | Meaning |
|---|---|
| **Available** | Vehicle can be booked |
| **In Use** | A trip is currently active for this vehicle |
| **Maintenance** | Vehicle is undergoing maintenance and cannot be booked |

---

## 8. Maintenance

### 8.1 Viewing Maintenance Records

- Navigate to **Maintenance** from the navbar.
- Records are paginated and filterable by status.

### 8.2 Scheduling Maintenance (Admin Only)

1. Click **"Schedule Maintenance"**.
2. Fill in:

| Field | Required | Validation |
|---|:---:|---|
| Vehicle | Yes | Select from vehicle list |
| Maintenance Type | Yes | Routine / Repair / Inspection / Tyre / Other |
| Description | Yes | Describe the maintenance work |
| Scheduled Date | Yes | Valid date |
| Estimated Cost (KES) | No | Must be non-negative if provided |
| Set vehicle to "Maintenance" now | No | Checkbox: immediately sets vehicle status |

3. Click **Schedule**.

#### ✅ Validation Checks
- Vehicle, type, description, and date are all required.
- Cost must be non-negative.
- If the checkbox is ticked, the vehicle status changes to **Maintenance** immediately (preventing new bookings).

### 8.3 Completing Maintenance (Admin Only)

- Click the ✔ Complete button on a maintenance record.
- Sets the completion date and returns the vehicle to **Available** status.

### 8.4 Cancelling Maintenance (Admin Only)

- Click the ✗ Cancel button.
- If the vehicle was in "Maintenance" status, it is returned to **Available**.

### 8.5 Deleting Maintenance (Admin Only)

- Click the 🗑 Delete button.
- **This action cannot be undone.**

---

## 9. Reports

### 9.1 Vehicle Trip Report

1. Navigate to **Reports > Vehicle Trip Report**.
2. Optionally filter by:
   - **Vehicle** (dropdown)
   - **Date Range** (From / To)
3. Click **Generate Report**.
4. View completed trip details: dates, routes, distance, fuel, cost.
5. Click **Export to Excel** to download an `.xlsx` file with formatted data and totals.

### 9.2 Budget & Fuel Cost Report

1. Navigate to **Reports > Budget Report**.
2. View fuel cost summary grouped by **Project Code**.
3. Table shows: Project Code, Number of Trips, Total Distance (km), Total Fuel (L), Total Fuel Cost (KES).

---

## 10. Calendar

- Navigate to **Calendar** from the navbar.
- View all bookings in an interactive calendar (powered by FullCalendar).
- **Colour coding:**
  - 🟡 **Yellow** = Pending bookings
  - 🟢 **Green** = Approved bookings

---

## 11. User Management (Admin Only)

### 11.1 Viewing Users

- Navigate to **Users** from the navbar.
- Users are listed with role, status, and registration date.
- Paginated at 20 users per page.

### 11.2 Editing a User

1. Click **Edit** on a user.
2. Update: Full Name, Email, Role, Active Status.
3. Click **Update User**.

#### ✅ Validation Checks
- Full name and email are required.
- Email must be unique (excluding the user being edited).
- Admin cannot deactivate their own account.
- Admin cannot remove their own admin role.

### 11.3 Resetting a User's Password

1. On the user edit page, scroll to **"Reset User Password"**.
2. Enter a new temporary password (minimum 6 characters).
3. Click **Reset Password**.
4. The user will be **forced to change their password** on next login.

### 11.4 Deleting a User

- Click **Delete** on the user list.
- **Warning:** This deletes all bookings and trips requested by the user and unassigns them as a driver from other bookings.
- Admin cannot delete their own account.
- **This action cannot be undone.**

---

## 12. Audit Log (Admin Only)

- Navigate to **Audit Log** from the navbar.
- View a chronological log of all system actions.
- Filter by:
  - **Entity Type:** User, Vehicle, Booking, Trip, Maintenance Record
  - **Action Type:** Create, Edit, Delete, Approve, Cancel, Assign, Complete
- Each entry shows: timestamp, user, action, entity, and details.

---

## 13. Profile & Password Management

### 13.1 Editing Your Profile

1. Click your name in the navbar, then **Profile**.
2. Update your **Full Name** or **Email**.
3. Click **Update Profile**.

#### ✅ Validation Checks
- Email must be unique (not used by another account).

### 13.2 Changing Your Password

1. Click your name in the navbar, then **Change Password**.
2. Fill in:

| Field | Requirement |
|---|---|
| Current Password | Must be correct |
| New Password | Minimum 6 characters, must differ from current |
| Confirm New Password | Must match new password |

3. Click **Change Password**.

#### ✅ Validation Checks
- Current password is verified before allowing the change.
- New password must be different from the current password.
- New password and confirmation must match.
- Minimum 6 characters.

---

## 14. Validation Rules Reference

### Quick Reference — All Validation Checks

| Area | Rule | Type |
|---|---|---|
| **Registration** | Username ≥ 3 chars, alphanumeric + dots/underscores | Server + Client |
| **Registration** | Username must be unique | Server |
| **Registration** | Email must be valid and unique | Server + Client |
| **Registration** | Password ≥ 6 characters | Server + Client |
| **Registration** | Passwords must match | Server + Client |
| **Login** | Both fields required | Client |
| **Login** | Deactivated accounts blocked | Server |
| **Login** | Rate limited: 10/minute | Server |
| **Password Reset** | Token expires after 24 hours | Server |
| **Password Reset** | Rate limited: 5/minute | Server |
| **Change Password** | Current password must be correct | Server |
| **Change Password** | New ≠ Current password | Server |
| **Change Password** | New password ≥ 6 characters | Server + Client |
| **Booking** | Vehicle required, not under maintenance | Server |
| **Booking** | Start date cannot be in the past | Server |
| **Booking** | End date must be after start date | Server + Client |
| **Booking** | Route From, Route To, Purpose are required | Server + Client |
| **Booking** | No scheduling conflict with same vehicle | Server |
| **Booking** | Re-checked at approval time | Server |
| **Trip Start** | Odometer ≥ 0 | Server + Client |
| **Trip Start** | Only for approved bookings without trip | Server |
| **Trip End** | End time > Start time | Server + Client |
| **Trip End** | Odometer End ≥ Odometer Start | Server + Client |
| **Trip End** | Fuel Used and Cost ≥ 0 (if provided) | Server + Client |
| **Vehicle** | Registration ≥ 3 chars, unique | Server + Client |
| **Vehicle** | Make and Model required | Server + Client |
| **Maintenance** | Vehicle, Type, Description, Date required | Server + Client |
| **Maintenance** | Cost ≥ 0 (if provided) | Server + Client |
| **User Edit** | Email must be unique (excluding self) | Server |
| **User Edit** | Cannot self-deactivate or self-demote | Server |
| **User Delete** | Cannot delete own account | Server |
| **All Forms** | CSRF token required | Server |

---

## 15. Email Notifications

Email notifications are sent automatically when enabled:

| Event | Who Gets Notified |
|---|---|
| New booking created | All active admins + the requester |
| Booking approved | The requester |
| Booking approved (with driver) | The assigned driver |
| Driver assigned or changed | The newly assigned driver |
| Booking cancelled | The requester + assigned driver (if any) |
| Password reset requested | The user who requested it |

> **Note:** Email notifications must be enabled by the administrator (environment variable `MAIL_ENABLED=1`).

---

## 16. Security Features

| Feature | Details |
|---|---|
| **CSRF Protection** | All forms include a security token to prevent cross-site request forgery |
| **Password Hashing** | Passwords are securely hashed; never stored in plain text |
| **Rate Limiting** | Login (10/min), Registration (5/min), Forgot Password (5/min) |
| **Session Timeout** | Automatic logout after **15 minutes** of inactivity; a warning appears at 14 minutes |
| **Forced Password Change** | Admin-reset accounts must change their password on first login |
| **Open Redirect Prevention** | Login redirects are validated to prevent malicious redirects |
| **Audit Trail** | All actions are logged with user, timestamp, and details |

---

## 17. Troubleshooting & FAQs

**Q: I get "The CSRF tokens do not match" error.**
A: Refresh the page and try again. This can happen if your session expired or the page was open too long.

**Q: I can't book a vehicle.**
A: Check that the vehicle is not under maintenance. Also, ensure your requested time does not conflict with an existing pending or approved booking.

**Q: I forgot my password.**
A: Click "Forgot your password?" on the login page. Enter your registered email, and a reset link will be sent.

**Q: My account is deactivated.**
A: Contact your administrator to reactivate your account.

**Q: I get "Rate limit exceeded" error.**
A: Wait a minute and try again. This is a security measure to prevent brute-force attacks.

**Q: I was logged out unexpectedly.**
A: The system automatically logs you out after 15 minutes of inactivity. Log in again to continue.

**Q: How do I export trip data?**
A: Go to **Reports > Vehicle Trip Report**, set your filters, and click **Export to Excel**.

---

*Vehicle Request Tracker — Plan International Kenya © 2026*
