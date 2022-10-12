frappe.views.calendar['Ticket Booking'] = {
    name:"Ticket Booking Date",
    field_map: {
        "start": "booking_date",
        "end": "booking_date",
        "id": "name",
        "allDay": "all_day",
        "title": "name",
        "color": "color",
        "status":1
    },
    gantt: true,
    order_by: 'name',
    get_css_class: function (data) {
        console.log(data);
        if (data.is_checked_in == 1) {
            return "success";
        } else {
            return "info"
        }
    }
}
