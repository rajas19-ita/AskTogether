const tabs = document.querySelectorAll(".at-btn-tabs");
const tabContents = document.querySelectorAll(".at-tab-content");
const unreadLoadingGif = document.getElementById("unread_loading_gif");
const readLoadingGif = document.getElementById("read_loading_gif");
const notificationSection = document.getElementById("notification-section");
let nextUnread = null;
let nextRead = null;

const switchTab = (button) => {
  let type = button.dataset.type;

  tabs.forEach((btn) => {
    btn.classList.remove("active");
    btn.ariaSelected = "false";
  });
  tabContents.forEach((tabC) => {
    tabC.classList.remove("active");
    tabC.hidden = true;
  });

  button.classList.add("active");
  button.ariaSelected = "true";
  const panel = document.getElementById(`${type}_panel`);
  panel.classList.add("active");
  panel.hidden = false;
};

const fetchNotifications = (type, next = null) => {
  return fetch(
    `${notificationSection.dataset.fetchUrl}?is_read=${type === "read"}${next ? `&cursor_id=${next}` : ""}`,
    {
      headers: {
        "X-CSRFToken": getCSRFToken(),
      },
    },
  )
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
      return data;
    })
    .catch((err) => {
      console.error(err);
    });
};

const loadMoreNotifications = (button, type) => {
  button.classList.add("at-hidden");
  if (type === "read") {
    document.getElementById(`${type}_panel`).append(readLoadingGif);
    readLoadingGif.classList.remove("at-hidden");
  } else {
    document.getElementById(`${type}_panel`).append(unreadLoadingGif);
    unreadLoadingGif.classList.remove("at-hidden");
  }
  fetchNotifications(type, type === "read" ? nextRead : nextUnread).then(
    (data) => {
      readLoadingGif.classList.add("at-hidden");
      unreadLoadingGif.classList.add("at-hidden");
      if (type === "read") {
        nextRead = data.next_cursor;
        renderReadNotifications(data.data);
      } else {
        nextUnread = data.next_cursor;
        renderUnreadNotifications(data.data);
      }
    },
  );
};

const renderReadNotifications = (data) => {
  const container = document.getElementById(`read_panel`);
  data.forEach((notification) => addNotificationToUI(notification, "read"));

  let loadMoreBtn = document.getElementById("load_more_read");
  if (data.length) {
    loadMoreBtn.classList.remove("at-hidden");
    container.appendChild(loadMoreBtn);
  } else {
    loadMoreBtn.classList.add("at-hidden");
  }
};

const renderUnreadNotifications = (data) => {
  const container = document.getElementById(`unread_panel`);
  console.log("unread_panel", container);

  data.forEach((notification) => addNotificationToUI(notification, "unread"));
  let loadMoreBtn = document.getElementById("load_more_unread");
  if (data.length) {
    loadMoreBtn.classList.remove("at-hidden");
    container.appendChild(loadMoreBtn);
  } else {
    loadMoreBtn.classList.add("at-hidden");
  }
};

const addNotificationToUI = (notification, type) => {
  const container = document.getElementById(`${type}_panel`);

  const wrapper = document.createElement("article");
  wrapper.className = "at-notification-card";

  wrapper.innerHTML = `
                ${notificationSVG(notification)}
                <div class="at-notification__content">
                    <p class="at-notification__message">
                        <a href=${notificationSection.dataset.notificationUrl.replace("0", notification.question.id)} target="_blank">
                            ${notification.message}
                        </a>
                    </p>
                    <time class="at-notification__time" data-dt="${notification.created_at}">
                        ${timeAgo(notification.created_at)}
                    </time>
                </div>
        `;
  container.appendChild(wrapper);
};

const notificationSVG = (notification) => {
  switch (notification.event_type) {
    case "ANSWER_POSTED":
      return `
                    <div class="at-notification-card__icon">
                        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-pencil-square" viewBox="0 0 16 16">
                            <path d="M15.502 1.94a.5.5 0 0 1 0 .706L14.459 3.69l-2-2L13.502.646a.5.5 0 0 1 .707 0l1.293 1.293zm-1.75 2.456-2-2L4.939 9.21a.5.5 0 0 0-.121.196l-.805 2.414a.25.25 0 0 0 .316.316l2.414-.805a.5.5 0 0 0 .196-.12l6.813-6.814z"/>
                            <path fill-rule="evenodd" d="M1 13.5A1.5 1.5 0 0 0 2.5 15h11a1.5 1.5 0 0 0 1.5-1.5v-6a.5.5 0 0 0-1 0v6a.5.5 0 0 1-.5.5h-11a.5.5 0 0 1-.5-.5v-11a.5.5 0 0 1 .5-.5H9a.5.5 0 0 0 0-1H2.5A1.5 1.5 0 0 0 1 2.5z"/>
                        </svg>
                    </div>`;
    case "COMMENT_ON_QUESTION":
    case "COMMENT_ON_ANSWER":
      return `
                    <div class="at-notification-card__icon mt-2">    
                        <svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" fill="currentColor" class="bi bi-chat-left" viewBox="0 0 16 16">
                            <path d="M14 1a1 1 0 0 1 1 1v8a1 1 0 0 1-1 1H4.414A2 2 0 0 0 3 11.586l-2 2V2a1 1 0 0 1 1-1zM2 0a2 2 0 0 0-2 2v12.793a.5.5 0 0 0 .854.353l2.853-2.853A1 1 0 0 1 4.414 12H14a2 2 0 0 0 2-2V2a2 2 0 0 0-2-2z"/>
                        </svg>
                    </div>`;
    case "ANSWER_SELECTED":
      return `
                    <div class="at-notification-card__icon mt-1">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="currentColor" width="34" height="34" viewBox="0 0 20 20" class="">
                            <path d="M8.294 16.998c-.435 0-.847-.203-1.111-.553L3.61 11.724a1.392 1.392 0 0 1 .27-1.951 1.392 1.392 0 0 1 1.953.27l2.351 3.104 5.911-9.492a1.396 1.396 0 0 1 1.921-.445c.653.406.854 1.266.446 1.92L9.478 16.34a1.39 1.39 0 0 1-1.12.656c-.022.002-.042.002-.064.002z"/>
                        </svg>
                    </div>`;
    case "UPVOTE_MILESTONE":
      return `
                    <div class="at-notification__badge mt-1">
                            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" fill="currentColor" class="bi bi-star-fill" viewBox="0 0 16 16">
                                <path d="M3.612 15.443c-.386.198-.824-.149-.746-.592l.83-4.73L.173 6.765c-.329-.314-.158-.888.283-.95l4.898-.696L7.538.792c.197-.39.73-.39.927 0l2.184 4.327 4.898.696c.441.062.612.636.282.95l-3.522 3.356.83 4.73c.078.443-.36.79-.746.592L8 13.187l-4.389 2.256z"/>
                            </svg>
                            <span>${notification.upvotes}</span>
                    </div>`;
  }
};

document.addEventListener("click", (e) => {
  const notificationTab = e.target.closest("[data-notification-tab]");
  if (notificationTab) {
    switchTab(notificationTab);
  }

  const loadMoreBtn = e.target.closest("[data-load-notification]");
  if (loadMoreBtn) {
    loadMoreNotifications(loadMoreBtn, loadMoreBtn.dataset.type);
  }
});

const fetchInitialNotifications = () => {
  readLoadingGif.classList.remove("at-hidden");
  unreadLoadingGif.classList.remove("at-hidden");
  Promise.all([fetchNotifications("read"), fetchNotifications("unread")]).then(
    (data) => {
      readLoadingGif.classList.add("at-hidden");
      unreadLoadingGif.classList.add("at-hidden");
      nextRead = data[0].next_cursor;
      nextUnread = data[1].next_cursor;

      if (data[0].data.length !== 0) {
        renderReadNotifications(data[0].data);
      } else {
        document.getElementById("no_read_msg").classList.remove("at-hidden");
      }
      if (data[1].data.length !== 0) {
        renderUnreadNotifications(data[1].data);
      } else {
        document.getElementById("no_unread_msg").classList.remove("at-hidden");
      }
    },
  );
};

fetchInitialNotifications();
