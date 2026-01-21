let allPosts = [];
let userProfile = document.getElementById("user-profile");

fetch(`${userProfile.dataset.fetchPosts}`)
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
    allPosts = data;
    renderPosts(data);
  })
  .catch((err) => {
    console.error(err);
    alert("Something went wrong, Please try again.");
  });

const renderPosts = (posts) => {
  const container = document.getElementById("post_container");

  container.innerHTML = "";

  const url = userProfile.dataset.questionUrl;

  posts.forEach((post, index) => {
    const wrapper = document.createElement("li");
    wrapper.innerHTML = `
                    <article class="at-profile-posts__item ${index !== posts.length - 1 ? "at-profile-posts__item--border" : ""}">
                        <span class="at-profile-posts__type">${post.type === "answer" ? "A" : "Q"}</span>
                        <a href="${url.replace("0", post.question_id)}" class="at-profile-posts__link">
                            ${post.title}
                        </a>
                        <time class="datetime" data-dt="${post.updated_at}">
                            ${new Date(post.updated_at).toLocaleString(
                              "en-US",
                              {
                                year: "numeric",
                                month: "short",
                                day: "numeric",
                              },
                            )}
                        </time>
                    </article>
                `;
    container.appendChild(wrapper);
  });
};

const filterPosts = (filter, button) => {
  if (button.classList.contains("active")) return;

  document
    .querySelectorAll(".lpost-filter-btn")
    .forEach((btn) => btn.classList.remove("active"));

  button.classList.add("active");

  if (filter === "all") {
    renderPosts(allPosts);
  } else {
    renderPosts(allPosts.filter((p) => p.type === filter));
  }
};

document.addEventListener("click", (e) => {
  const postsFilterBtn = e.target.closest("[data-posts-filter]");
  if (postsFilterBtn) {
    filterPosts(postsFilterBtn.dataset.type, postsFilterBtn);
  }
});
