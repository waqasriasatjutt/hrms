==============================
POS Auto Send Mail – Odoo 18
============================

.. image:: banner.png
:alt: POS Auto Send Mail Banner
:align: center

# Overview

**POS Auto Send Report** is an Odoo 18 module that automatically sends a daily sales report by email at a scheduled time.
The report includes all POS sessions and their sales details for the day, allowing management and stakeholders to stay updated without manually extracting reports.

# Key Features

* Automatically emails daily POS sales reports at a fixed scheduled time.
* Includes detailed session information such as:

  * Total sales
  * Payment breakdown
  * Tax information
  * Products sold
* Runs automatically through Odoo's scheduled actions (cron).
* No manual intervention required once configured.
* Easily customizable email template.
* Suitable for single or multi-company environments.

# Installation

1. Add the module to your Odoo addons folder.
2. Activate **Developer Mode** in Odoo.
3. Go to **Apps → Update Apps List**.
4. Search for *POS Auto Send Mail* and click **Install**.

# Configuration

1. Ensure your outgoing mail server (SMTP) is configured:
   **Settings → General Settings → Outgoing Mail Servers**
2. Go to:
   **Settings → Technical → Scheduled Actions**
3. Look for:
   *POS Daily Report Email*
4. Set:

   * Active: Yes
   * Execution Time: Choose your preferred daily schedule
5. (Optional) Customize the email template:
   **Settings → Technical → Email → Templates**
   Template name: *Daily POS Sales Report*

# How It Works

* Every day at the scheduled time, the system checks all closed POS sessions.
* It generates the consolidated sales report for the day.
* The report is automatically emailed to the configured recipients.
* Fully automatic once initial configuration is completed.

# Requirements

* Odoo 18 Community or Enterprise
* Working SMTP configuration

# Support & Contact

For support, customization, or professional implementation services, contact:

# License

AGPL-3 (or update to your preferred license)

# Changelog

**Version 1.0.0**

* First release
* Automatic daily POS email reporting via scheduled action
* Template customization support


