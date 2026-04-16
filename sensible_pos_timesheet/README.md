# Sensible POS Timesheet

## Overview

The **Sensible POS Timesheet** module seamlessly integrates HR attendance functionality with Point of Sale (POS) operations. This powerful integration automatically tracks employee working hours during POS sessions, providing real-time timer display and comprehensive attendance management for retail operations.

## Key Features

### 🕐 Automatic Time Tracking
- **Auto Check-in**: Automatically creates attendance records when POS session opens
- **Auto Check-out**: Automatically closes attendance records when POS session ends
- **Real-time Timer**: Live timer display in POS interface showing current session duration

### ⚙️ Configuration Control
- **Enable/Disable**: Toggle timesheet creation from POS configuration settings
- **Per POS**: Configure timesheet tracking individually for each POS terminal
- **Smart Integration**: Uses Odoo's standard attendance methods for reliability

### 📊 Attendance Management
- **Smart Button**: View all attendance records directly from POS session
- **Session Linking**: Each attendance record is linked to its corresponding POS session
- **Comprehensive Tracking**: Complete audit trail of working hours per session

### 🖥️ User Interface
- **POS Timer Widget**: Non-intrusive timer display in POS navbar
- **Visual Feedback**: Clear indication when timesheet is active
- **Seamless Integration**: Natural part of the POS workflow

## Installation

1. Download and place the module in your Odoo addons directory
2. Update your apps list
3. Install the module from Apps menu
4. Configure POS settings to enable timesheet creation

## Configuration

### Enable Timesheet Creation

1. Navigate to **Point of Sale > Configuration > Point of Sale**
2. Select the desired POS configuration
3. In the settings, enable **"Create Timesheet"**
4. Save the configuration

### User Setup

1. Ensure POS users have associated employee records
2. Verify HR attendance permissions are properly configured
3. Test the integration with a sample session

## Usage

### Starting a POS Session

1. When opening a POS session with timesheet enabled:
   - System automatically creates an attendance check-in
   - Timer widget appears in POS interface
   - Real-time tracking begins

### During POS Session

- Timer displays current session duration
- Attendance is automatically linked to the POS session
- No manual intervention required

### Closing a POS Session

1. When closing the POS session:
   - System automatically creates attendance check-out
   - Timer stops and disappears
   - Complete attendance record is saved

### Viewing Attendance Records

1. From POS session form view:
   - Click the **"Attendance"** smart button
   - View all related attendance records
   - Access detailed time tracking information

## Technical Details

### Dependencies
- `point_of_sale`: Core POS functionality
- `hr_attendance`: Attendance tracking system  
- `hr`: Human Resources management
- `pos_hr`: POS-HR integration bridge

### Models Extended
- **pos.config**: Added timesheet creation toggle
- **pos.session**: Enhanced with attendance tracking capabilities
- **hr.attendance**: Linked to POS sessions for better organization

### Security
- Proper access rights for POS users
- Secure integration with HR attendance system
- Multi-company support included

## Troubleshooting

### Common Issues

**Timer not appearing**
- Verify timesheet creation is enabled in POS config
- Check if user has an associated employee record
- Ensure proper permissions are granted

**Attendance not created**
- Confirm employee record exists for the user
- Check HR attendance module is installed and configured
- Verify POS session opened with timesheet-enabled configuration

**Missing attendance records**
- Check the smart button on POS session form
- Verify attendance records are properly linked
- Review system logs for any error messages

## Support & Contact

### 🐛 Bug Reporting
If you encounter any issues, please contact us at **info@sensiblecs.com**. We're committed to continuously improving our tools.

### 💡 Feature Requests
Share your ideas and feature requests with us. If they align with public use cases, we'll prioritize them in our development roadmap at no additional cost.

### 🆘 General Support  
For questions or concerns, don't hesitate to reach out at **info@sensiblecs.com**. We're here to help you get the most out of this module.

---

**Developed by [Sensible Consulting Services](https://www.sensiblecs.com)**

*Enhancing your Odoo experience with intelligent business solutions*