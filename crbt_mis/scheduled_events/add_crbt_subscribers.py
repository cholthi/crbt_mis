#!/usr/bin/env python3

import frappe
import pandas as p
import  crbt_mis.utils as utils


def add_cbrt_subscribers():
    """Adds the data to the CRBT MIS system. The data must be add in this order
    - Add Artists
    - Add Subscribers
    - Add Content
    - Add Artist Profile
    - Attach content to artist
    - Add subscribers

    The data file with subscribers information is downloaded from a remote impa server
    """
    excel_obj = utils.get_data_obj_from_email()
    df = p.read_excel(excel_obj, sheet_name='Sheet0')

   # Upload artist profile
    utils.upload_artist_profile(df)
   # Upload Artist
    utils.upload_artist(df)
    # Upload subscribers to crbt content
    utils.upload_subscribers(df)
    # Upload content
    utils.upload_artist_content(df)
    # Link content to their artist. very important for report generation
    utils.attach_content_to_artist(df)
    # Link subscribers to content. The most important doctype in the system
    utils.upload_content_subscribers(df)

