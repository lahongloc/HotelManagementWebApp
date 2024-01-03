const search = () => {
    kw = document.getElementById('kw').value
    checkIn = document.getElementById('check_in_date').value
    checkOut = document.getElementById('check_out_date').value
    roomType = document.querySelector('.room-type').id

    fetch('/api/search', {
        method: 'POST',
        body: JSON.stringify({
            kw,
            checkIn,
            checkOut,
            roomType
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(res => res.json())
        .then(data => {
            console.log(data)
        })
        .catch(err => console.error(err))
}