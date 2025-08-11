# Copyright (c) 2025, Philip Chol and contributors
# For license information, please see license.txt

import frappe
import datetime


def execute(filters=None):
    columns = get_columns()
    data = get_data(filters)
    report_summary = get_summary(data)
    return columns, data, '', [], report_summary

def get_data(filters):
    username = frappe.session.user
    artist_doc = frappe.db.get_list("Artist", filters={"user_id": username}, fields=["artist_code", "name"])
    if artist_doc:
        artist = artist_doc[0]["artist_code"]
    else:
        artist = 'None'
    start_date = filters.get("from_date")
    now = datetime.datetime.today().date()
    end_date = filters.get("to_date", now.strftime("%Y-%m-%d"))
    plan = filters.get("plan")
    conditions = []

    if artist:
        conditions.append(f"cs.artist = '{artist}'")
    if plan:
        conditions.append(f"cs.tarrif_id = '{plan}'")
    if start_date:
        conditions.append(f"cs.date BETWEEN '{start_date}' AND '{end_date}'")
    where_clause = " WHERE " + " AND ".join(conditions) if conditions else ""

    query = f"""SELECT c.content_title, cs.content_id, COUNT(amount) as subscribers, SUM(amount) as revenue
               FROM `tabContent Subscriber` as cs
               INNER JOIN  `tabArtist Content` as ac
               ON  cs.content_id = ac.name
               INNER JOIN  `tabContent` as c
               ON ac.content_id = c.name
               {where_clause}
               GROUP BY cs.content_id
             """
    data = frappe.db.sql(query, as_dict=True)
    return data

def get_columns():
    return [
            {"label": "Content Title", "fieldname": "content_title", "fieldtype": "Data", "width": 150},
            {"label": "Content ID", "fieldname": "content_id", "fieldtype": "Data", "width": 200},
            {"label": "Subscribers", "fieldname": "subscribers", "fieldtype": "Int", "width": 150},
            {"label": "Revenue (SSP)", "fieldname": "revenue", "fieldtype": "Float", "width": 150},
        ]

def get_summary(data):
    total = sum([row["revenue"] for row in data])
    summary = [{
        "value": total,
        "indicator": "Green" if total > 0 else "Red",
        "label": "Total CRBT revenue",
        "datatype": "Currency",
        "currency": "SSP"
        }]
    return summary

