let roomTypes = document.querySelectorAll('.room-type-dropdown > li')
let customerTypes = document.querySelectorAll('.customer-type')
const customerContainer = document.getElementById("customer-box");

roomTypes.forEach((item, index) => {
    item.addEventListener('click', () => {
        document.querySelector('.room-type-name').innerText = item.innerText
//        document.querySelector('.room-type-name').id=
    })
})

customerTypes.forEach(customerType => {
    customerType.addEventListener('click', () => {
        document.querySelector('.customer-type-name').innerText = customerType.innerHTML
    })
})

const addNewCustomer = () => {
    let order = document.querySelectorAll('.customer-info').length + 1

    let newCusInfo = document.createElement('div');
    newCusInfo.className = 'customer-info d-flex mb-2';
    newCusInfo.innerHTML = `
            <label>
                <span class="me-4 order">${order}</span>
                <input placeholder="Tên khách hàng"/>
            </label>
            <span>
                <button type="button" class="btn dropdown-toggle customer-type-name" data-bs-toggle="dropdown">
                    Loại khách
                </button>
                <ul class="dropdown-menu">
                    <li class="dropdown-item customer-type">Nội địa</li>
                    <li class="dropdown-item customer-type">Nước ngoài</li>
                </ul>
            </span>
            <label>
                <input type="number" placeholder="CMND/CCCD"/>
            </label>
            <label>
                <input placeholder="Địa chỉ"/>
            </label>
            <span onClick="removeCustomerInfo(event)" style="margin-right: 16px; padding: 4px; color: #f15a5a; cursor:pointer">
                <i class="fa-solid fa-x"></i>
            </span>
    `;

    customerContainer.insertBefore(newCusInfo, customerContainer.lastElementChild);
}

const removeCustomerInfo = (event) => {
    let customerInfos = document.querySelectorAll('.customer-info')
    if (customerInfos.length > 1) {
        let customerInfo = event.target.closest('.customer-info')

        if (customerInfo) {
            const orderSpan = customerInfo.querySelector('.order');
            const order = parseInt(orderSpan.innerText, 10);

            customerInfo.remove();

            customerInfos.forEach((customerInfo, idx) => {
                if (idx > order - 1)
                    customerInfo.querySelector('.order').innerText = (idx).toString()
            })
        }
    }
}

