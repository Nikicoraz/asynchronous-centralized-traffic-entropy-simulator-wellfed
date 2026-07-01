const auth = document.getElementById("auth");
const urlInput = document.getElementById("url");
const targetInput = document.getElementById("target");

// Se l'utente aveva già inserito il jwt rimettilo nell'input
let jwt = localStorage.getItem("jwt");
if (jwt) {
  auth.value = jwt;
}

let url = localStorage.getItem("url");
if (url) {
  urlInput.value = url;
} else {
  url = "/";
}

let target = localStorage.getItem("target");
if (target) {
  targetInput.value = target;
} else {
  target = "backend";
}

// Salva solo quando cambia il focus
auth.addEventListener("change", (e) => {
  localStorage.setItem("jwt", auth.value);
  jwt = auth.value;
});

urlInput.addEventListener("change", (e) => {
  localStorage.setItem("url", urlInput.value);
  url = urlInput.value;
});

targetInput.addEventListener("change", (e) => {
  localStorage.setItem("target", targetInput.value);
  target = targetInput.value;
});

// Intercetta richieste form
Array.from(document.getElementsByTagName("form")).forEach((form) => {
  form.addEventListener("formdata", (e) => {
    e.preventDefault();

    e.formData.append("jwt", jwt);
    e.formData.append("url", url);
    e.formData.append("target", target);
  });
});
