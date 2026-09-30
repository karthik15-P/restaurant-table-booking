function validateBookingForm() {
    const phone = document.getElementById("phone");
    const guests = document.getElementById("guests");

    if (phone && !/^\d{10}$/.test(phone.value.trim())) {
        alert("Please enter a valid 10-digit phone number.");
        phone.focus();
        return false;
    }

    if (guests && (parseInt(guests.value) < 1 || parseInt(guests.value) > parseInt(guests.max))) {
        alert(`Guests must be between 1 and ${guests.max}.`);
        guests.focus();
        return false;
    }

    return true;
}
