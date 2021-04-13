const yearSelect = document.getElementById("income-year");
const monthSelect = document.getElementById("income-month");
const daySelect = document.getElementById("income-day");

const monthOptions = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November","December"];
const yearStart = 2010
const yearEnd = 2040

if (typeof income_year !== 'undefined') { // Edit income item was selected

    for (var i = yearStart; i <= yearEnd; i++) {
        var yOption = i;
        var newElement = document.createElement("option");
        newElement.textContent = yOption;
        newElement.value = yOption;
        yearSelect.appendChild(newElement)
    }
    yearSelect.value = income_year

    for(var i = 0; i < monthOptions.length; i++) {
        var mOption = monthOptions[i];
        var newElement = document.createElement("option");
        newElement.textContent = mOption;
        newElement.value = mOption;
        monthSelect.appendChild(newElement);
    }
    monthSelect.value = monthOptions[income_month - 1];

    while (daySelect.length > 0) {
        daySelect.remove(0)
    }
    var numberOfDays = getDays(income_month, income_year)

    for(var i = 1; i <= numberOfDays; i++) {
        var dOption = i;
        var newElement = document.createElement("option");
        newElement.textContent = dOption;
        newElement.value = dOption;
        daySelect.appendChild(newElement);
    }
    daySelect.value = income_day;

} else { // Edit income item was not selected
    for (var i = yearStart; i <= yearEnd; i++) {
        var yOption = i;
        var newElement = document.createElement("option");
        newElement.textContent = yOption;
        newElement.value = yOption;
        yearSelect.appendChild(newElement)
    }
}

function months() {
    for(var i = 0; i < monthOptions.length; i++) {
        var mOption = monthOptions[i];
        var newElement = document.createElement("option");
        newElement.textContent = mOption;
        newElement.value = mOption;
        monthSelect.appendChild(newElement);
    }
}

function days() {
    while (daySelect.length > 0) {
        daySelect.remove(0)
    }
    var selectedYear = yearSelect.options[yearSelect.selectedIndex].value;
    var selectedMonth = monthSelect.options[monthSelect.selectedIndex].value;
    var numberOfDays = getDays(monthOptions.indexOf(selectedMonth) + 1, parseInt(selectedYear))

    for(var i = 1; i <= numberOfDays; i++) {
        var dOption = i;
        var newElement = document.createElement("option");
        newElement.textContent = dOption;
        newElement.value = dOption;
        daySelect.appendChild(newElement);
    }
}

function getDays(month, year) {
    return new Date(year, month, 0).getDate();
}
