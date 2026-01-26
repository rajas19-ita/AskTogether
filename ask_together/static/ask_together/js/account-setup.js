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

const setMessage = ({ type, text, enableSubmit }) => {
  messageEl.classList.toggle(
    "account-setup__message--success",
    type === "success",
  );
  messageEl.classList.toggle(
    "account-setup__message--danger",
    type === "danger",
  );
  messageEl.textContent = text;
  selectBtn.disabled = !enableSubmit;
};

async function checkUsername(username) {
  const u = (username ?? "").trim();

  if (!u) {
    setMessage({
      type: "danger",
      text: "username is required",
      enableSubmit: false,
    });

    return;
  }

  const params = new URLSearchParams({ username: u });

  try {
    const res = await fetch(`${usernameCheckUrl}?${params.toString()}`);

    const data = await pJson(res);

    if (data.available) {
      setMessage({
        type: "success",
        text: `username '${u}' is available`,
        enableSubmit: true,
      });
    } else {
      setMessage({
        type: "danger",
        text: `username '${u}' is taken`,
        enableSubmit: false,
      });
    }
  } catch (err) {
    console.error(err);
    notyfCenter.error("Something went wrong, Please try again.");
  }
}

const debouncedCheckUsername = debouncedFunction(checkUsername, 300);

const handleChange = (e) => {
  debouncedCheckUsername(e.target.value);
};

usernameInput.addEventListener("input", handleChange);
