frappe.listview_settings['Online Ticket Booking'] = {
    get_indicator: function(doc) {
        if (doc.booking_status == 'Confirmed') {
            return [__("Confirmed"), "green"];
        } else if (doc.booking_status == 'Cancelled') {
            return [__("Cancelled"), "red"];
        }
    },
}
