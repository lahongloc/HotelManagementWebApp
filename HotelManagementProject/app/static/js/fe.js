let roomTypes = document.querySelectorAll('.room-type-dropdown > li')
roomTypes.forEach((item, index) => {
    item.addEventListener('click',() => {
        document.querySelector('.room-type-name').innerText = item.innerText
    })
})