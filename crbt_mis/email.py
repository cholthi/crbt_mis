#!/usr/bin/env python3
"""
Module: imap_email_fetcher.py
Description: Fetches emails from an IMAP server, filters messages with subject matching given param received today,
             and reads attachments.
Complies with PEP 8 standards and uses helper functions.
"""

import imaplib
import email
from email.header import decode_header, make_header
from datetime import datetime, timezone
from typing import List, Tuple, Optional


def connect_to_imap_server(host: str, username: str, password: str) -> imaplib.IMAP4_SSL:
    """Connects to the IMAP server and logs in."""
    mail = imaplib.IMAP4_SSL(host)
    mail.login(username, password)
    return mail


def fetch_emails(mail: imaplib.IMAP4_SSL, folder: str = 'INBOX') -> List[bytes]:
    """Selects the folder and fetches all email UIDs."""
    mail.select(folder)
    result, data = mail.uid('search', None, 'ALL')
    if result != 'OK' or not data or not data[0]:
        return []
    email_uids = data[0].split()
    return email_uids


def parse_email_date(date_str: str) -> Optional[datetime]:
    """Parses the email date string to a datetime object in UTC."""
    from email.utils import parsedate_to_datetime

    try:
        dt = parsedate_to_datetime(date_str)
    except Exception:
        return None

    if dt is None:
        return None

    if dt.tzinfo is None:
        # Assume UTC if no timezone info
        dt = dt.replace(tzinfo=timezone.utc)
    else:
        dt = dt.astimezone(timezone.utc)
    return dt


def email_received_today(email_msg) -> bool:
    """Checks if the email was received today (UTC based)."""
    date_str = email_msg.get('Date', '')
    if not date_str:
        return False
    email_date = parse_email_date(date_str)
    if email_date is None:
        return False

    now_utc = datetime.now(timezone.utc)
    return email_date.date() == now_utc.date()


def subject_matches(email_msg, subject_param: str) -> bool:
    """Checks if the subject of the email matches the given subject_param (case-insensitive substring search)."""
    subject_header = email_msg.get('Subject', '')
    if not subject_header:
        return False
    decoded_subject = str(make_header(decode_header(subject_header)))
    return subject_param.lower() in decoded_subject.lower()


def extract_attachments(email_msg) -> List[Tuple[str, bytes]]:
    """
    Extracts attachments from the email message.

    Returns:
        List of tuples (filename, content_bytes)
    """
    attachments = []

    for part in email_msg.walk():
        content_disposition = part.get("Content-Disposition", None)
        if content_disposition and 'attachment' in content_disposition.lower():
            filename = part.get_filename()
            if filename:
                # Decode filename if encoded
                filename = str(make_header(decode_header(filename)))
            else:
                filename = 'unknown'

            payload = part.get_payload(decode=True)
            if payload is not None:
                attachments.append((filename, payload))

    return attachments


def fetch_emails_with_subject_today(
    host: str,
    username: str,
    password: str,
    subject_param: str,
    folder: str = 'INBOX',
) -> List[Tuple[email.message.Message, List[Tuple[str, bytes]]]]:
    """
    Connects to the IMAP server, fetches emails from folder,
    returns list of tuples (email_message, attachments) where
    subject matches subject_param and email received today.
    """
    mail = connect_to_imap_server(host, username, password)
    email_uids = fetch_emails(mail, folder)
    matched_emails = []

    for uid in email_uids:
        result, data = mail.uid('fetch', uid, '(RFC822)')
        if result != 'OK':
            continue

        raw_email = data[0][1]
        email_msg = email.message_from_bytes(raw_email)

        if subject_matches(email_msg, subject_param) and email_received_today(email_msg):
            attachments = extract_attachments(email_msg)
            matched_emails.append((email_msg, attachments))

    mail.logout()
    return matched_emails


# Example usage (uncomment and fill credentials to use):
# if __name__ == '__main__':
#     HOST = 'imap.example.com'
#     USER = 'user@example.com'
#     PASSWORD = 'yourpassword'
#     SUBJECT_PARAM = 'Your subject keyword'
#     emails_with_attachments = fetch_emails_with_subject_today(HOST, USER, PASSWORD, SUBJECT_PARAM)
#     for msg, attachments in emails_with_attachments:
#         print(f"Subject: {msg.get('Subject')}")
#         print(f"Date: {msg.get('Date')}")
#         print(f"Number of attachments found: {len(attachments)}")
#         for filename, content in attachments:
#             print(f"Attachment: {filename} ({len(content)} bytes)")
#         print('-' * 40)

