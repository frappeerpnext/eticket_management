// Copyright (c) 2023, Tes Pheakdey and contributors
// For license information, please see license.txt

frappe.ui.form.on('POS Backup', {
	refresh: function(frm) {
		frm.disable_save('dgaw')
		frm.set_intro(__("Please Click Backup To Backup POS System Data"), false);
		
		frm.add_custom_button('Backup', () => {
			frm.save()
		})
		frm.change_custom_button_type('Backup', null, 'primary');
	}
	
});
	

