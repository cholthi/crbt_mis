// Copyright (c) 2025, Philip Chol and contributors
// For license information, please see license.txt

frappe.ui.form.on("Artist", {
 	refresh(frm) {
		if (frappe.user.has_role("Administrator")) {
			frm.add_custom_button("Assign Content", () => {
				frappe.new_doc('Artist Content', {
					artist: frm.doc.name
			})	
		})
	}

 },
});
