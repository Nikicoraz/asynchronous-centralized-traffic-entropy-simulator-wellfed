const operationInput = document.getElementById("operation");
const errorRateInput = document.getElementById("error_rate");

const prepareDataButton = document.getElementById("prepare_data");
prepareDataButton.addEventListener("click", async (e) => {
    prepareDataButton.disabled = true;
    const response = await fetch("/prepare_data", {
        method: "POST",
        body: ""
    });

    if (response.status != 200) {
        prepareDataButton.disabled = false;
    }
});

let operation = localStorage.getItem("operation");
if (operation) {
    operationInput.value = operation;
} else {
    operation = "RegisterClient";
}

let errorRate = localStorage.getItem("errorRate");
if (errorRate) {
    errorRateInput.value = errorRate;
} else {
    errorRateInput.value = 0;
}

operationInput.addEventListener("change", (e) => {
    localStorage.setItem("operation", operationInput.value);
    operation = operationInput.value;
});

errorRateInput.addEventListener("change", (e) => {
    localStorage.setItem("errorRate", errorRateInput.value);
    errorRate = errorRateInput.value;
});

// Intercetta richieste form
Array.from(document.getElementsByTagName("form")).forEach((form) => {
  form.addEventListener("formdata", (e) => {
    e.preventDefault();

    e.formData.append("operation", operation);
    e.formData.append("errorRate", parseInt(errorRate));
    const parsedErrorRate = parseInt(errorRate, 10);
    e.formData.append("errorRate", isNaN(parsedErrorRate) ? 0 : parsedErrorRate);
  });
});