let roomTypes = document.querySelectorAll('.room-type-dropdown > li')
roomTypes.forEach((item, index) => {
    item.addEventListener('click',() => {
        document.querySelector('.room-type-name').innerText = item.innerText
//        document.querySelector('.room-type-name').id=
    })
})

cus_types = document.getElementsByClassName('cus_type')
cus_types.forEach((item, index) => {
       console.log(item)
//    if(item.value == 'DOMESTIC') {
//        item.checked = true
//    }
})

