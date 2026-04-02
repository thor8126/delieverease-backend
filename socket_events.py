from flask_socketio import emit, join_room, leave_room


def register_socket_events(socketio):
    """Register Socket.IO event handlers for real-time rider location tracking."""

    @socketio.on("connect")
    def handle_connect():
        print("Client connected")

    @socketio.on("disconnect")
    def handle_disconnect():
        print("Client disconnected")

    @socketio.on("join_order")
    def handle_join_order(data):
        """Customer joins a room to watch rider location for their order."""
        order_id = data.get("order_id")
        if order_id:
            room = f"order_{order_id}"
            join_room(room)
            print(f"Client joined room: {room}")

    @socketio.on("leave_order")
    def handle_leave_order(data):
        """Customer leaves the order tracking room."""
        order_id = data.get("order_id")
        if order_id:
            room = f"order_{order_id}"
            leave_room(room)
            print(f"Client left room: {room}")

    @socketio.on("rider_location_update")
    def handle_rider_location(data):
        """
        Rider emits their location. Data: { order_id, lat, lng }
        Server broadcasts to everyone watching that order.
        """
        order_id = data.get("order_id")
        lat = data.get("lat")
        lng = data.get("lng")

        if order_id and lat is not None and lng is not None:
            room = f"order_{order_id}"
            emit("location_update", {
                "order_id": order_id,
                "lat": lat,
                "lng": lng,
            }, room=room, include_self=False)
