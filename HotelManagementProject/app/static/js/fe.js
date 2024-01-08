let roomTypes = document.querySelectorAll(".room-type-dropdown > li");
roomTypes.forEach((item, index) => {
  item.addEventListener("click", () => {
    document.querySelector(".room-type-name").innerText = item.innerText;
  });
});

const validateDateTime = () => {
    const checkinTime = new Date(document.getElementById('checkin').value)
    const checkoutTime = new Date(document.getElementById('checkout').value)
    if(checkoutTime <= checkinTime) {

        alert("Checkout time must be after checkin time 1.");
        document.getElementById('checkin').value = ''
        document.getElementById('checkout').value = ''
    }
}

const flash = () => {
  document.querySelector('.auto-fill').classList.add('animate__flash')
  setInterval(() => {
    document.querySelector('.auto-fill').classList.remove('animate__flash')
  }, 1500)
}

