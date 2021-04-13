/* Inventory Items element */
const materialsItems = document.querySelector('#materials');

materialsItems.addEventListener('click', decreaseQuantity);
materialsItems.addEventListener('click', increaseQuantity);

/* Display new decreased quantity */
function decreaseQuantity(e) {
    //e.preventDefault();

    if (e.target.classList.contains('decrease-button')) {
        const materialId = (e.target).value
        const materialQuantity = (e.target).nextSibling.nextSibling

        req = $.ajax({
            url : 'materials/item_decrease_quantity',
            type : 'POST',
            data : {material_id : materialId},
            success: function(response){
                new_quantity = response.quantity;
                materialQuantity.innerText = new_quantity
            }
        });
    }
}

/* Display new increased quantity */
function increaseQuantity(e) {
    //e.preventDefault();

    if (e.target.classList.contains('increase-button')) {
        const materialId = (e.target).value
        const materialQuantity = (e.target).previousSibling.previousSibling

        req = $.ajax({
            url : 'materials/item_increase_quantity',
            type : 'POST',
            data : {material_id : materialId},
            success: function(response){
                new_quantity = response.quantity;
                materialQuantity.innerText = new_quantity;
            }
        });
    }
}
