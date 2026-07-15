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

document.querySelectorAll("form").forEach((form) => {
    form.addEventListener("submit", async (e) => {
        e.preventDefault(); 

        const statusMessage = document.getElementById('status');
        const actionUrl = form.getAttribute("action");

        const rawFormData = new FormData(form);
        const formData = new URLSearchParams();

        for (const [key, value] of rawFormData.entries()) {
            formData.append(key, value);
        }

        const currentOperation = operationInput.value;
        const parsedErrorRate = parseInt(errorRateInput.value);
        const currentErrorRate = isNaN(parsedErrorRate) ? 0 : parsedErrorRate;

        formData.append('operation', currentOperation);
        formData.append('errorRate', currentErrorRate);

        statusMessage.style.transition = "none";
        statusMessage.style.opacity = "1";
        statusMessage.style.display = "block"; 

        try {
            const response = await fetch(actionUrl, {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                statusMessage.style.color = "green";
                statusMessage.textContent = "Requests queued";
            } else {
                statusMessage.style.color = "red";
                statusMessage.textContent = `Server Error (${response.status})`;
            }
        } catch (error) {
            statusMessage.style.color = "red";
            statusMessage.textContent = "Error during request";
            console.error("Fetch error:", error);
        }

        setTimeout(() => {
            statusMessage.style.transition = "opacity 0.8s ease";
            statusMessage.style.opacity = "0";

            setTimeout(() => {
                if (statusMessage.style.opacity === "0") {
                    statusMessage.style.display = "none";
                }
            }, 800);

        }, 2000);
    });
});