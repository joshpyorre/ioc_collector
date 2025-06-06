// Function to display the map with the provided data
function displayMap(mapData) {
    var map = L.map('map').setView([0, 0], 2);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 18,
    }).addTo(map);

    var srcIcon = L.icon({
        iconUrl: '/static/images/redskull.png',  // Path to your custom icon
        iconSize: [30, 30],  // Size of the icon
        iconAnchor: [15, 30],  // Point of the icon which will correspond to marker's location
        popupAnchor: [0, -30],  // Point from which the popup should open relative to the iconAnchor
    });

    // Group the data by lat/lon coordinates
    const groupedData = mapData.reduce((acc, item) => {
        const key = `${item.lat},${item.lon}`;
        if (!acc[key]) {
            acc[key] = { count: 0, description: item.description, lat: item.lat, lon: item.lon };
        }
        acc[key].count += 1;
        return acc;
    }, {});

    // Place markers on the map
    Object.values(groupedData).forEach(function (location) {
        // Extract city and country from description
        const descriptionParts = location.description.split(' (Domain: ')[0];

        // Format the popup content as "City, Country, URLs: count"
        const popupContent = `${descriptionParts}, URLs: ${location.count}`;

        L.marker([location.lat, location.lon], { icon: srcIcon })
            .bindPopup(popupContent)
            .addTo(map);
    });
}

// This would be populated from your FastAPI backend
const mapData = window.mapData || [];
if (mapData.length > 0) {
    displayMap(mapData);
}

// Initialize the map when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', function () {
    if (window.mapData) {
        // Initialize the map
        const map = L.map('map').setView([20, 0], 2); // Centered globally

        // Add OpenStreetMap tiles
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 18,
            attribution: '© OpenStreetMap'
        }).addTo(map);

        // Add markers
        window.mapData.forEach(location => {
            L.marker([location.lat, location.lon])
                .addTo(map)
                .bindPopup(location.description);
        });
    }
});

// Function to generate array of random colors for the chart
function generateColors(count) {
    const colors = [];
    for (let i = 0; i < count; i++) {
        const color = `hsl(${Math.floor(Math.random() * 360)}, 70%, 50%)`;
        colors.push(color);
    }
    return colors;
}

// Initialize the pie chart if data is available
if (typeof chartData !== 'undefined') {
    const ctx = document.getElementById('countryChart').getContext('2d');
    const countryChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: chartData.labels,
            datasets: [{
                data: chartData.values,
                backgroundColor: generateColors(chartData.values.length),
                borderColor: '#ffffff',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: 'right',
                },
                title: {
                    display: true,
                    text: 'IP Distribution by Country'
                }
            }
        }
    });
}
