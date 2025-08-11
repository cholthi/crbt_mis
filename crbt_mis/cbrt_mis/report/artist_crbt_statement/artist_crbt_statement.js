// Copyright (c) 2025, Philip Chol and contributors
// For license information, please see license.txt

frappe.query_reports["Artist CRBT Statement"] = {
	"filters": [
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
