const usernameInput = document.getElementById("username_select");
const usernameCheckUrl = usernameInput.dataset.usernameUrl;
const messageEl = document.getElementById("username_message");
const selectBtn = document.getElementById("username_select_btn");

const debouncedFunction = (callback, delay) => {
  let timeoutId;
  return (...args) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => {
      callback(...args);
    }, delay);
  };
};

const handleUsernameCheck = (username) => {
  fetch(`${usernameCheckUrl}?username=${username}`)
    .then((res) => {
      if (res.ok) {
        return res.json();
      } else {
        return res.json().then((err) => {
          throw err;
        });
      }
    })
    .then((data) => {
      let available = data.available;

      if (available) {
        messageEl.classList.remove("account-setup__message--danger");
        messageEl.classList.add("account-setup__message--success");
        messageEl.innerHTML = `username '${username}' is available`;
        selectBtn.disabled = false;
      } else {
        messageEl.classList.add("account-setup__message--danger");
        messageEl.classList.remove("account-setup__message--success");
        messageEl.innerHTML = `username '${username}' is taken`;
        selectBtn.disabled = true;
      }
    })
    .catch((err) => {
      if (err.error === "username query param is required") {
        messageEl.classList.add("account-setup__message--danger");
        messageEl.classList.remove("account-setup__message--success");
        messageEl.innerHTML = `username is required`;
        selectBtn.disabled = true;
      } else {
        console.log(err);
        alert("something went wrong, please try again.");
      }
    });
};

const debouncedUsernameCheck = debouncedFunction(handleUsernameCheck, 300);

const handleChange = (e) => {
  debouncedUsernameCheck(e.target.value);
};

usernameInput.addEventListener("input", handleChange);
