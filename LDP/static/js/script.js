// Function to get normal range for each feature
function getNormalRange(feature) {
    var normalRanges = {
        "feature1": { min: 0, max: 120 },
        "feature2": { min: 0, max: 5 },
        "feature3": { min: 0, max: 500 },
        "feature4": { min: 0, max: 100 },
        "feature5": { min: 0, max: 100 },
        "feature6": { min: 0, max: 100 },
        "feature7": { min: 0, max: 20 },
        "feature8": { min: 0, max: 10 },
        "feature9": { min: 0, max: 1 },
        "feature10": { min: 0, max: 1 }
    };

    return normalRanges[feature] || { min: 0, max: Infinity };
}

document.addEventListener('DOMContentLoaded', function() {
    var predictionForm = document.getElementById('prediction-form');
    var modal = document.getElementById('myModal');
    var modalContent = document.getElementById('modalContent');
    var submitFeedbackUrl = "/submit_feedback/";

    predictionForm.addEventListener('submit', function(event) {
        event.preventDefault();

        // Validate the form before sending
        if (!validateForm()) {
            return; // Prevent form submission if validation fails
        }

        var formData = new FormData(predictionForm);
        var xhr = new XMLHttpRequest();
        xhr.open('POST', '/predict/', true);
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');

        var csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
        xhr.setRequestHeader('X-CSRFToken', csrfToken);

        xhr.onreadystatechange = function() {
            if (xhr.readyState === XMLHttpRequest.DONE) {
                if (xhr.status === 200) {
                    var responseData = JSON.parse(xhr.responseText);
                    if (responseData.prediction === 1) {
                        modalContent.textContent = "You may have liver disease.";
                    } else if (responseData.prediction === 2) {
                        modalContent.textContent = "You may not have liver disease.";
                    } else {
                        modalContent.textContent = 'Prediction Result: ' + responseData.prediction;
                    }

                    modal.style.display = 'block';

                    // Show and update the download report link
                    if (responseData.prediction_id) {
                        var downloadBtn = document.getElementById("downloadReportBtn");
                        console.log("Prediction ID: ", responseData.prediction_id); // Log to verify the ID
                        downloadBtn.href = `/download/${responseData.prediction_id}/`;
                        downloadBtn.style.display = "inline-block"; // Make it visible
                    }

                } else {
                    console.error('Request failed. Status:', xhr.status);
                }
            }
        };

        xhr.onerror = function() {
            console.error('Request failed. Network error');
        };

        xhr.send(formData);
    });

    var closeBtn = document.getElementsByClassName('close')[0];
    closeBtn.addEventListener('click', function(event) {
        event.preventDefault();
        modal.style.display = 'none';
        var predictionResult = modalContent.textContent;
        document.getElementById('predictionResult').textContent = predictionResult;


        var downloadBtn = document.getElementById("downloadReportBtn");
        if (downloadBtn.href && downloadBtn.href !== window.location.href + "#") {
        downloadBtn.style.display = "inline-block";
        }
        });

    

    // Validate form fields
    function validateForm() {
        var isValid = true;
        var fields = predictionForm.querySelectorAll('input[type="text"]');
        fields.forEach(function(field) {
            var value = parseFloat(field.value);
            var range = getNormalRange(field.name);
            if (value < range.min || value > range.max) {
                displayValidationMessage(field, 'Value should be between ' + range.min + ' and ' + range.max);
                isValid = false;
            } else {
                clearValidationMessage(field);
            }
        });
        return isValid;
    }

    // Display validation messages next to the fields
    function displayValidationMessage(field, message) {
        var validationMessage = field.nextElementSibling;
        validationMessage.textContent = message;
    }

    // Clear any previous validation messages
    function clearValidationMessage(field) {
        var validationMessage = field.nextElementSibling;
        validationMessage.textContent = '';
    }
});
