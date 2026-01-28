const tabs = document.querySelectorAll(".at-btn-tabs");
const tabContents = document.querySelectorAll(".at-tab-content");
const unreadLoadingGif = document.getElementById("unread_loading_gif");
const readLoadingGif = document.getElementById("read_loading_gif");
const notificationSection = document.getElementById("notification-section");

const state = {
  read: { next: null, loadingGif: readLoadingGif },
  unread: { next: null, loadingGif: unreadLoadingGif },
};

const keyPanel = (type) => document.getElementById(`${type}_panel`);
const keyLoadMore = (type) => document.getElementById(`load_more_${type}`);
const keyEmptyMsg = (type) => document.getElementById(`no_${type}_msg`);

function switchTab(button) {
  let type = button.dataset.type;

  tabs.forEach((btn) => {
    let active = btn === button;
    btn.classList.toggle("active", active);
    btn.ariaSelected = String(active);
  });

  tabContents.forEach((panel) => {
    let active = panel.id === `${type}_panel`;
    panel.classList.toggle("active", active);
    panel.hidden = !active;
  });
}

async function fetchNotifications(type, cursor = null) {
  const baseUrl = notificationSection.dataset.fetchUrl;
  const params = new URLSearchParams({
    is_read: String(type === "read"),
  });

  if (cursor) params.set("cursor_id", cursor);

  const res = await fetch(`${baseUrl}?${params.toString()}`, {
    headers: { "X-CSRFToken": getCSRFToken() },
  });

  const data = await pJson(res);

  return data;
}

function setLoading(type, isLoading) {
  const panel = keyPanel(type);
  const gif = state[type].loadingGif;

  if (!panel || !gif) return;

  gif.classList.toggle("at-hidden", !isLoading);
  if (isLoading) panel.append(gif);
}

function addNotificationToUI(notification, type) {
  const container = keyPanel(type);
  if (!container) return;

  const wrapper = document.createElement("article");
  wrapper.className = "at-notification-card";

  wrapper.insertAdjacentHTML("beforeend", notificationSVG(notification));

  const content = document.createElement("div");
  content.className = "at-notification__content";

  const p = document.createElement("p");
  p.className = "at-notification__message";

  const a = document.createElement("a");
  // a.target = "_blank";
  a.href = notificationSection.dataset.notificationUrl.replace(
    "0",
    notification.question.id,
  );
  a.textContent = notification.message;

  p.appendChild(a);

  const time = document.createElement("time");
  time.className = "at-notification__time";
  time.dataset.dt = notification.created_at;
  time.textContent = timeAgo(notification.created_at);

  content.append(p, time);
  wrapper.appendChild(content);
  container.appendChild(wrapper);
}

function renderNotifications(type, notifications, has_more) {
  notifications.forEach((n) => addNotificationToUI(n, type));

  const loadMoreBtn = keyLoadMore(type);
  const panel = keyPanel(type);

  if (!loadMoreBtn || !panel) return;

  loadMoreBtn.classList.toggle("at-hidden", !has_more);
  panel.appendChild(loadMoreBtn);
}

async function loadMoreNotifications(type, button) {
  button.classList.add("at-hidden");
  setLoading(type, true);

  try {
    const data = await fetchNotifications(type, state[type].next);
    state[type].next = data.next_cursor;

    renderNotifications(type, data.data, data.has_more);
  } catch (err) {
    console.error(err);
    button.classList.remove("at-hidden");
  } finally {
    setLoading(type, false);
  }
}

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
    loadMoreNotifications(loadMoreBtn.dataset.type, loadMoreBtn);
  }
});

async function fetchInitialNotifications() {
  setLoading("read", true);
  setLoading("unread", true);

  try {
    const [read, unread] = await Promise.all([
      fetchNotifications("read"),
      fetchNotifications("unread"),
    ]);

    state.read.next = read.next_cursor;
    state.unread.next = unread.next_cursor;

    if (read.data.length) renderNotifications("read", read.data, read.has_more);
    else keyEmptyMsg("read")?.classList.remove("at-hidden");

    if (unread.data.length)
      renderNotifications("unread", unread.data, unread.has_more);
    else keyEmptyMsg("unread")?.classList.remove("at-hidden");
  } catch (err) {
    console.error(err);
  } finally {
    setLoading("read", false);
    setLoading("unread", false);
  }
}

fetchInitialNotifications();
