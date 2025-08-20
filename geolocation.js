function getLocation(callback) {
    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                const coords = {
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude
                };
                callback(coords);
            },
            (error) => {
                callback({error: error.message});
            }
        );
    } else {
        callback({error: "Geolocation not supported"});
    }
}

window.getLocation = getLocation;