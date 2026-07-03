const jwtInput = document.getElementById("auth");
const methodInput = document.getElementById("method");
const endpointInput = document.getElementById("endpoint");
const errorRateInput = document.getElementById("error_rate");

// Se l'utente aveva già inserito il jwt rimettilo nell'input
let jwt = localStorage.getItem("jwt");
if (jwt) {
  jwtInput.value = jwt;
} else {
  jwt = "";
}

let method = localStorage.getItem("method");
if (method) {
    methodInput.value = method;
} else {
    method = "GET";
}

let endpoint = localStorage.getItem("endpoint");
if (endpoint) {
  endpointInput.value = endpoint;
} else {
  endpoint = "/";
}

let errorRate = localStorage.getItem("errorRate");
if (errorRate) {
    errorRateInput.value = errorRate;
} else {
    errorRateInput.value = 0;
}

// Salva solo quando cambia il focus
jwtInput.addEventListener("change", (e) => {
  localStorage.setItem("jwt", jwtInput.value);
  jwt = jwtInput.value;
});

methodInput.addEventListener("change", (e) => {
    localStorage.setItem("method", methodInput.value);
    method = methodInput.value;
});

endpointInput.addEventListener("change", (e) => {
  localStorage.setItem("endpoint", endpointInput.value);
  endpoint = endpointInput.value;
});

errorRateInput.addEventListener("change", (e) => {
    localStorage.setItem("errorRate", errorRateInput.value);
    errorRate = errorRate.value;
});

// Intercetta richieste form
Array.from(document.getElementsByTagName("form")).forEach((form) => {
  form.addEventListener("formdata", (e) => {
    e.preventDefault();

    e.formData.append("jwt", jwt);
    e.formData.append("method", method);
    e.formData.append("endpoint", endpoint);
    e.formData.append("errorRate", errorRate);
  });
});