#!/usr/bin/env python3

import frappe
import io
from crbt_mis.email import fetch_emails_with_subject_today
from datetime import datetime


@frappe.whitelist()
def get_subs():
    subs = frappe.get_list('Subscriber', limit=5)
    return subs

def get_data_obj_from_email():
    """ Read attachment from imap server
    """
    host = frappe.conf.imap_host
    username = frappe.conf.imap_username
    password = frappe.conf.imap_password
    search_param = frappe.conf.match_str
    email_attachments = fetch_emails_with_subject_today(
            host,
            username,
            password,
            search_param
            )
    if not email_attachments:
        return None
    for msg, att in email_attachments:
        if not att:
            return None
        excel_buffer = io.BytesIO(att[0][1])
        return excel_buffer

def upload_artist_content(pandas_df):
    """Upload artist content to frappe Content doctype
    """
    for _, row in pandas_df.iterrows():
        new_content = frappe.new_doc("Content")
        new_content.content_id = row["CONTENT_ID"]
        new_content.song_id = row["SONGID"]
        new_content.content_title = row["CONTENT_NAME"]
        new_content.insert(ignore_if_duplicate=True)
    frappe.db.commit()
    return

def upload_artist_profile(pandas_df):
    """Upload artist profile to frappe Artist Profile doctype
    """
    filtered_artists = pandas_df[pandas_df['ARTIST'].notnull()]
    for _, row in filtered_artists.iterrows():
        try:
            new_profile = frappe.new_doc("Artist Profile")
            artist_code = row["ARTIST"]
            new_profile.artist_name = row["ARTIST"]
            new_profile.artist_code = row["ARTIST"]
            new_profile.insert(ignore_if_duplicate=True)
        except frappe.UniqueValidationError as uve:
            continue
    frappe.db.commit()
    return

def get_tarrifs():
    """Return tarrits set in frappe Tarrif Plan doctype
    """
    db_tarrifs = frappe.db.get_list("Tarrif Plan", fields=["tarrif_name", "tarrif_rate"])
    tarrifs = dict()
    for tarrif in db_tarrifs:
        tarrifs[str(int(tarrif["tarrif_rate"]))] = tarrif["tarrif_name"]
    return tarrifs


def upload_content_subscribers(pandas_df):
    """Upload content subscribers to frappe Content Subscriber doctype
    """
    filtered_df = pandas_df[pandas_df[['ARTIST', 'CONTENT_ID', 'CHARGING_AMOUNT', "TO_CHAR(REQUEST_TIME,'YYYY-MM-DD')"]].notnull().all(1)]
    tarrif_map = get_tarrifs()
    for _, row in filtered_df.iterrows():
        try:
            c_s = frappe.new_doc("Content Subscriber")
            content_id = "{}-{}".format(row["ARTIST"],row["CONTENT_ID"])
            c_s.content_id = content_id
            c_s.subscriber_id = row["MSISDN"]
            tarrif = tarrif_map[str(row["CHARGING_AMOUNT"])]
            c_s.tarrif_id = tarrif
            c_s.operation = "Activation"
            d_format = "%Y-%m-%d"
            c_s.date = datetime.strptime(row["TO_CHAR(REQUEST_TIME,'YYYY-MM-DD')"], d_format).date()
            if not c_s.docstatus.is_submitted():
                c_s.submit()
            frappe.db.commit()
        except frappe.LinkValidationError as e:
            frappe.db.rollback()
            continue
        except frappe.DuplicateEntryError as de:
            continue
    return


def upload_artist(pandas_df):
    """Create an artist based on data from panda dateframe
    """
    filtered_artists = pandas_df[pandas_df['ARTIST'].notnull()]
    for _, row in filtered_artists.iterrows():
        exist = frappe.db.exists("Artist", {"artist_code": row["ARTIST"]})
        if not exist:
            new_artist = frappe.new_doc("Artist")
            new_artist.artist_name = row["ARTIST"]

            # Get artist profile
            try:
                artist_profile = frappe.get_doc("Artist Profile", {"artist_code": row["ARTIST"]})
                new_artist.artist_profile = artist_profile.name
            except frappe.DoesNotExistError as e:
                pass
            new_artist.insert()
    frappe.db.commit()
    return

def attach_content_to_artist(pandas_df):
    """Associate artist profile to content. This is how we know which
    artist owns which content
    """
    filtered_df = pandas_df[pandas_df[['ARTIST', 'CONTENT_ID',]].notnull().all(1)]
    for _, row in filtered_df.iterrows():
        exist = frappe.db.exists("Artist Content", {"artist": row["ARTIST"], "content_id": row["CONTENT_ID"]})

        if not exist:
            try:
                new_ac = frappe.new_doc("Artist Content")
                new_ac.content_id = row["CONTENT_ID"]
                new_ac.artist = row["ARTIST"]
                new_ac.insert()
                frappe.db.commit()
            except frappe.LinkValidationError as le:
                continue
    return

def upload_subscribers(pandas_df):
    """Add CRBT subscribers members. Typically, these are MSISDNs from the telecom
    """
    filtered_msisdns = pandas_df[pandas_df['MSISDN'].notnull()]
    for _, row in filtered_msisdns.iterrows():
        try:
            new_sub = frappe.new_doc("Subscriber")
            new_sub.msisdn = row["MSISDN"]
            new_sub.type = "Phone"
            new_sub.insert(ignore_if_duplicate=True)
            frappe.db.commit()
        except frappe.DuplicateEntryError as de:
            continue
    return
