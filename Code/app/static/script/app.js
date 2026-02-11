function toggleManual(showManual) {
    document.getElementById("manualLocation").style.display =
        showManual ? "block" : "none";
    document.getElementById("autoLocation").style.display =
        showManual ? "none" : "block";
}

function getLocation() {
    if (!navigator.geolocation) {
        alert("Geolocation not supported");
        return;
    }

    navigator.geolocation.getCurrentPosition(
        pos => {
            document.getElementById("latitude").value = pos.coords.latitude;
            document.getElementById("longitude").value = pos.coords.longitude;
            document.getElementById("locationStatus").innerText =
                "Location captured successfully ✔";
        },
        () => {
            alert("Location access denied");
        }
    );
}
