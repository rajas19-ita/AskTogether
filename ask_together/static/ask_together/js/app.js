function formatUTCtoLocal(root = document, selector = ".datetime") {
  root.querySelectorAll(selector).forEach((el) => {
    const dt = new Date(el.dataset.dt);
    el.textContent = dt.toLocaleString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    });
  });
}

function timeAgo(dateString) {
  const now = new Date();
  const past = new Date(dateString);

  const seconds = Math.floor((now - past) / 1000);

  const intervals = [
    { label: "year", seconds: 31536000 },
    { label: "month", seconds: 2592000 },
    { label: "day", seconds: 86400 },
    { label: "hour", seconds: 3600 },
    { label: "minute", seconds: 60 },
    { label: "second", seconds: 1 },
  ];

  for (const interval of intervals) {
    const count = Math.floor(seconds / interval.seconds);
    if (count > 0) {
      return `${count} ${interval.label}${count > 1 ? "s" : ""} ago`;
    }
  }
  return "just now";
}

function getCSRFToken() {
  return document.cookie
    .split("; ")
    .find((row) => row.startsWith("csrftoken="))
    ?.split("=")[1];
}

const notyfCenter = new Notyf({
  position: {
    x: "center",
    y: "top",
  },
});

function setSavedUI(button, saved) {
  button.dataset.saved = String(saved);
  button.setAttribute(
    "aria-label",
    saved ? "Unsave Question" : "Save Question",
  );
}

async function pJson(res) {
  let data = null;
  if (res.ok) {
    data = await res.json();
  } else {
    const err = await res.json();
    throw err;
  }
  return data;
}

async function saveQuestion(button) {
  if (button.disabled) return;

  const wasSaved = button.dataset.saved === "true";
  const url = button.dataset.url;
  const method = wasSaved ? "DELETE" : "POST";

  button.disabled = true;

  try {
    const res = await fetch(url, {
      method,
      headers: {
        "X-CSRFToken": getCSRFToken(),
      },
    });

    const data = await pJson(res);

    setSavedUI(button, data.saved);
    notyfCenter.success(data.saved ? "Question Saved" : "Question Unsaved");
  } catch (err) {
    setSavedUI(button, wasSaved);
    notyfCenter.error("Some error occurred");
  } finally {
    button.disabled = false;
  }
}

async function fetchUnreadNotificationsCount(url) {
  try {
    const res = await fetch(url);

    const data = await pJson(res);

    if (data.count <= 0) return;

    let countEl = document.getElementById("header_notification_count");

    countEl.textContent = String(data.count);
    countEl.classList.remove("at-hidden");
  } catch (err) {
    console.error(err);
  }
}

// sidebar close

const sidebar = document.querySelector(".at-sidebar");
const overlay = document.querySelector(".at-sidebar-overlay");
const closeBtn = document.querySelector(".at-sidebar-close");

function closeSidebar() {
  sidebar?.classList.remove("open");
  overlay?.classList.remove("active");
}

sidebar?.addEventListener("click", (e) => {
  if (e.target.closest("a")) closeSidebar;
});
overlay?.addEventListener("click", closeSidebar);
closeBtn?.addEventListener("click", closeSidebar);

document.addEventListener("click", (e) => {
  const saveBtn = e.target.closest("[data-save]");

  if (saveBtn) {
    saveQuestion(saveBtn, saveBtn.dataset.id);
  }
});
