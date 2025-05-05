var map = L.map('map').setView([45.383402, -71.932936], 13); // Centré sur Paris
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
}).addTo(map);

var markers = [];
var polylines = [];

map.on('click', function(e) {
    var demand = parseInt(document.getElementById('demand').value);
    fetch('/add_waypoint', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ lat: e.latlng.lat, lon: e.latlng.lng, demand: demand })
    }).then(response => response.json()).then(data => {
        updateWaypoints();
    });
});

function updateWaypoints() {
    fetch('/get_waypoints')
        .then(response => response.json())
        .then(waypoints => {
            markers.forEach(marker => map.removeLayer(marker));
            markers = [];
            waypoints.forEach(wp => {
                var marker = L.marker([wp.lat, wp.lon])
                    .bindPopup(`Demande: ${wp.demand}`)
                    .addTo(map);
                markers.push(marker);
            });
        });
}

function optimizeRoute() {
    var num_vehicles = parseInt(document.getElementById('num_vehicles').value);
    var vehicle_capacity = parseInt(document.getElementById('vehicle_capacity').value);
    fetch('/optimize_route', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ num_vehicles: num_vehicles, vehicle_capacity: vehicle_capacity })
    })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }
            polylines.forEach(poly => map.removeLayer(poly));
            polylines = [];
            data.routes.forEach((route, index) => {
                var color = ['blue', 'red', 'green', 'purple'][index % 4];
                var polyline = L.polyline(route.map(p => [p.lat, p.lon]), { color: color }).addTo(map);
                polylines.push(polyline);
                map.fitBounds(polyline.getBounds());
            });
        });
}

updateWaypoints();