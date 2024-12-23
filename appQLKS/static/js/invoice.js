// Function to calculate the totals
    function calculateTotals() {
        let totalDefaultCust = 0;
        let totalOtherCust = 0;

        // Loop through each room detail and sum the values
        {% for rd in details %}
        totalDefaultCust += {{ rd.num_of_default_cust }};
        totalOtherCust += {{ rd.num_of_other_cust }};
        {% endfor %}

        // Set the calculated totals in the hidden input fields
        document.getElementById('total_default_cust').value = totalDefaultCust;
        document.getElementById('total_other_cust').value = totalOtherCust;
    }

    // Call the calculateTotals function when the form is submitted
    document.getElementById('submitDetails').onclick = function() {
        calculateTotals(); // Calculate totals before submitting
    };