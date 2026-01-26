let allPosts = [];
const userProfile = document.getElementById("user-profile");
const container = document.getElementById("post_container");

async function apiGetPosts(url) {
  const res = await fetch(url);
  const data = await pJson(res);
  return data;
}

const formatDate = (iso) =>
  new Date(iso).toLocaleString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  });

function buildPostItem(post, isLast, questionUrlTemplate) {
  const li = document.createElement("li");

  const article = document.createElement("article");
  article.className = `at-profile-posts__item ${
    isLast ? "" : "at-profile-posts__item--border"
  }`;

  const badge = document.createElement("span");
  badge.className = "at-profile-posts__type";
  badge.textContent = post.type === "answer" ? "A" : "Q";

  const a = document.createElement("a");
  a.className = "at-profile-posts__link";
  a.href = questionUrlTemplate.replace("0", post.question_id);
  a.textContent = post.title ?? "";

  const time = document.createElement("time");
  time.className = "datetime";
  time.dataset.dt = post.updated_at;
  time.textContent = formatDate(post.updated_at);

  article.append(badge, a, time);

  li.appendChild(article);

  return li;
}

function renderPosts(posts) {
  container.textContent = "";

  const questionUrlTemplate = userProfile.dataset.questionUrl;
  const frag = document.createDocumentFragment();

  posts.forEach((post, idx) => {
    frag.appendChild(
      buildPostItem(post, idx === posts.length - 1, questionUrlTemplate),
    );
  });

  container.appendChild(frag);
}

async function initPosts() {
  try {
    const data = await apiGetPosts(userProfile.dataset.fetchPosts);

    allPosts = Array.isArray(data) ? data : [];
    renderPosts(allPosts);
  } catch (err) {
    console.error(err);
    notyfCenter.error("Something went wrong, Please try again.");
  }
}

function setActiveFilter(button) {
  document
    .querySelectorAll(".lpost-filter-btn.active")
    .forEach((btn) => btn.classList.remove("active"));

  button.classList.add("active");
}

function filterAndRender(filter) {
  if (filter === "all") return renderPosts(allPosts);
  renderPosts(allPosts.filter((p) => p.type === filter));
}

document.addEventListener("click", (e) => {
  const postsFilterBtn = e.target.closest("[data-posts-filter]");
  if (!postsFilterBtn) return;

  if (postsFilterBtn.classList.contains("active")) return;

  setActiveFilter(postsFilterBtn);
  filterAndRender(postsFilterBtn.dataset.type);
});

initPosts();
