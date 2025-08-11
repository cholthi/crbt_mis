// Copyright (c) 2025, Philip Chol and contributors
// For license information, please see license.txt

frappe.query_reports["CRBT Statement"] = {
	"filters": [
	{
            fieldname: "artist",
            label: __("Artist Name"),
            fieldtype: "Link",
            options: "Artist"
        },
	{
            fieldname: "plan",
            label: __("Tarrif Plan"),
            fieldtype: "Link",
            options: "Tarrif Plan"
        },
	{
            fieldname: "from_date",
            label: __("Start Date"),
            fieldtype: "Date"
        },
	{
            fieldname: "to_date",
            label: __("End Date"),
            fieldtype: "Date"
        },

	]
};
