frappe.views.calendar['Event'] = {
    field_map: {
        start: 'booking_date',
        end: 'booking_date',
        id: 'name',
        allDay: 'all_day',
        title: 'name'
    },
    style_map: {
        Public: 'success',
        Private: 'info'
    },
    order_by: 'name',
}
