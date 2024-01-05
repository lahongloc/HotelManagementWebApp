let roomTypes = document.querySelectorAll(".room-type-dropdown > li");
roomTypes.forEach((item, index) => {
  item.addEventListener("click", () => {
    document.querySelector(".room-type-name").innerText = item.innerText;
    //        document.querySelector('.room-type-name').id=
  });
});
// count = 1;
// const addCustomer = (capacity, roleCus) => {
//   count++
//   document.querySelector(
//     "div.rest-customer"
//   ).innerHTML += `<label class="mt-3"><b>CUSTOMER </b></label>
//                         <label style="display: block;" class="mt-1" for="cus${count}">Name</label>
//                         <input name="customerName${count}" id="cus${count}" type="text" class="form-control mt-2">

//                         <label style="display: block;" class="mt-2" for="cus${count}-type">Customer Type</label>
//                         <select class="form-control mt-2" name="customerType${count}" id="cus${count}-type">
                            
//                             {% for r in role_cus %}
//                             <option>{{ r }}</option>
//                             {% endfor %}
//                         </select>`;
// };
