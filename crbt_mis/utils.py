#!/usr/bin/env python3

import frappe


@frappe.whitelist()
def get_subs():
    subs = frappe.get_list('Subscriber', limit=5)
    return subs
