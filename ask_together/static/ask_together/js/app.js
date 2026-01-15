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

function saveQuestion(button) {
  const wasSaved = button.dataset.saved === "true";
  const url = button.dataset.url;
  const method = wasSaved ? "DELETE" : "POST";

  button.dataset.saved = (!wasSaved).toString();
  button.setAttribute(
    "aria-label",
    wasSaved ? "Save question" : "Unsave question"
  );
  button.disabled = true;

  fetch(url, {
    method,
    headers: {
      "X-CSRFToken": getCSRFToken(),
    },
  })
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
      button.dataset.saved = data.saved.toString();
      button.setAttribute(
        "aria-label",
        !data.saved ? "Save question" : "Unsave question"
      );

      notyfCenter.success(
        data.saved === true ? "Question Saved" : "Question Unsaved"
      );
    })
    .catch((err) => {
      button.dataset.saved = wasSaved.toString();
      button.setAttribute(
        "aria-label",
        wasSaved ? "Unsave question" : "Save question"
      );

      notyfCenter.error("Some error occurred");
    })
    .finally(() => {
      button.disabled = false;
    });
}

function fetchUnreadNotificationsCount(url) {
  fetch(url)
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
      if (data.count !== 0) {
        let countEl = document.getElementById("header_notification_count");
        countEl.innerHTML = data.count;
        countEl.classList.remove("at-hidden");
      }
    })
    .catch((err) => {
      console.error(err);
    });
}

document.addEventListener("DOMContentLoaded", () => {
  const sidebar = document.querySelector(".at-sidebar");
  const overlay = document.querySelector(".at-sidebar-overlay");

  sidebar?.addEventListener("click", (e) => {
    if (e.target.closest("a")) {
      sidebar?.classList.remove("open");
      overlay?.classList.remove("active");
    }
  });

  overlay?.addEventListener("click", () => {
    sidebar?.classList.remove("open");
    overlay.classList.remove("active");
  });

  document
    .querySelector(".at-sidebar-close")
    ?.addEventListener("click", (e) => {
      sidebar?.classList.remove("open");
      overlay?.classList.remove("active");
    });
});
