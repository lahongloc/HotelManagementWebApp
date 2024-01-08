let roomTypes = document.querySelectorAll(".room-type-dropdown > li");
roomTypes.forEach((item, index) => {
  item.addEventListener("click", () => {
    document.querySelector(".room-type-name").innerText = item.innerText;
  });
});



const flash = () => {
  document.querySelector('.auto-fill').classList.add('animate__flash')
  setInterval(() => {
    document.querySelector('.auto-fill').classList.remove('animate__flash')
  }, 1500)
}

