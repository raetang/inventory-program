/* Inventory Items element */
const inventoryItems = document.querySelector('#inventory');

inventoryItems.addEventListener('click', decreaseQuantity);
inventoryItems.addEventListener('click', increaseQuantity);

/* Display new decreased quantity */
function decreaseQuantity(e) {
    //e.preventDefault();

    if (e.target.classList.contains('decrease-button')) {
        const itemId = (e.target).value
        const itemQuantity = (e.target).nextSibling.nextSibling

        req = $.ajax({
            url : 'inventory/item_decrease_quantity',
            type : 'POST',
            data : {item_id : itemId},
            success: function(response){
                new_quantity = response.quantity;
                itemQuantity.innerText = new_quantity
            }
        });
    }
}

/* Display new increased quantity */
function increaseQuantity(e) {
    //e.preventDefault();

    if (e.target.classList.contains('increase-button')) {
        const itemId = (e.target).value
        const itemQuantity = (e.target).previousSibling.previousSibling

        req = $.ajax({
            url : 'inventory/item_increase_quantity',
            type : 'POST',
            data : {item_id : itemId},
            success: function(response){
                new_quantity = response.quantity;
                itemQuantity.innerText = new_quantity;
            }
        });
    }
}
