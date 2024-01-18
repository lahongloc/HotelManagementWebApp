let roomType
const takeRoomType = (obj) => {
    roomType = obj.id
}
const search = () => {
    kw = document.getElementById('kw').value
    checkIn = document.getElementById('check_in_date').value
    checkOut = document.getElementById('check_out_date').value

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

let country = "DOMESTIC"

function GetCountry()
{
    var message = document.getElementById('show_message');
    message.innerHTML = "You are a domestic customer";
    type = document.getElementById('countryType2');
    if (type.value === 'DOMESTIC'){
        message.innerHTML = "You are a domestic customer";
    }
    else if (type.value === 'FOREIGN'){
        message.innerHTML = "You are a foreign customer";
    }
    country = type.value
}

const UserRegister = () => {
    name = document.getElementById('name').value
    username = document.getElementById('username').value
    password = document.getElementById('password').value
    confirm = document.getElementById('confirm').value
    email = document.getElementById('email').value
    phone = document.getElementById('phone').value


    fetch('/api/register', {
        method: 'POST',
        body: JSON.stringify({
            country,
            name,
            username,
            password,
            confirm,
            email,
            phone
        }),
        headers: {
            'Content-Type': 'application/json'
        }
    })
        .then(res => res.json())
        .then(data => {
            console.log(data)
        //    if (!(data.code === 200)) {
        //        alert('Notice: ' + data.err_msg)
        //        document.querySelector("#register-Btn").href = '/register'
        //    } else {
        //        alert('Notice: registered successfully')
        //        document.querySelector("#register-Btn").href = '/login'
        //        document.querySelector("#register-Btn").click()
        //    }
        //     console.log(data.code)
        })
        .catch(err => console.error(err))
}

// xử lý forgot password

// pay the reservation
const payForReservation = (room_id, reservationInfo) => {
    if(confirm('Pay 30% for this room reservation?') === true){
        fetch('/api/reservation-paying', {
            method: 'POST',
            body: JSON.stringify({
                room_id,
                reservationInfo
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(res => res.json())
            .then(data => {
                window.location.href = '/';
                console.log(data)
            })
            .catch(err => console.error(err))

    }

}

const checkin = (reservationId, roomName) => {
    if(confirm(`Are you sure you want to check in to room ${roomName}?`) === true) {
        fetch('/api/room-renting', {
            method: 'POST',
            body: JSON.stringify({
               reservationId
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(res => res.json())
            .then(data => {
                if(data.code === 200) {
                    location.reload()
                }
            })
            .catch(err => console.error(err))
    }
}

const checkout = (roomRentalId, roomName, roomId) => {
    if(confirm(`Are you sure you want to check in to room ${roomName}?`) === true) {
        fetch('/api/room-checkout', {
            method: 'POST',
            body: JSON.stringify({
               roomRentalId,
               roomId
            }),
            headers: {
                'Content-Type': 'application/json'
            }
        })
            .then(res => res.json())
            .then(data => {
                if(data.code === 200) {
                    location.reload()
//                     window.location.href = 'http://127.0.0.1:5000/payment';
                }
            })
            .catch(err => console.error(err))
    }
}

const createRoomRental = (identification) => {
    fetch('/api/create-room-rental', {
        method: 'POST',
        body: JSON.stringify({
            identification
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

