const formEl = document.getElementById("answer_form");

function addAnswerToUI(answer) {
  const container = document.getElementById("answer_container");
  container.insertAdjacentHTML("beforeend", answer);
  formatUTCtoLocal(container);
}

function removeFormError(formEl) {
  formEl.querySelector(".at-error-msg")?.remove();
}

function clearSummernote() {
  const iframe = document.getElementById("id_content_iframe");
  const editable = iframe.contentDocument.querySelector(".note-editable");
  if (editable) {
    editable.innerHTML = "";
  }
}

function showFormError(formEl, message) {
  removeFormError(formEl);

  const p = document.createElement("p");
  p.className = "at-error-msg at-form-error mb-1";
  p.textContent = message;
  formEl.appendChild(p);
}

function incrementAnswerCount() {
  const countEl = document.getElementById("answer_count");
  if (!countEl) return;

  let current = parseInt(countEl.textContent);

  if (isNaN(current)) return;

  let newCount = current + 1;
  countEl.textContent = `${newCount} Answer${newCount !== 1 ? "s" : ""}`;
}

async function handleAnswerSubmit(e) {
  try {
    e.preventDefault();

    const url = formEl.dataset.url;
    const questionId = Number.parseInt(formEl.dataset.id, 10);
    const value = formEl.querySelector("#id_content").value;
    const answer = value?.trim() ?? "";

    if (!answer) {
      showFormError(formEl, "Answer cannot be empty");
      return;
    }

    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken(),
      },
      body: JSON.stringify({
        content: answer,
        question: questionId,
      }),
    });

    const data = await pJson(res);

    removeFormError(formEl);
    formEl.reset();
    clearSummernote();

    incrementAnswerCount();
    addAnswerToUI(data.html);
  } catch (err) {
    const msg = err?.content?.[0] || "Some error occurred";
    showFormError(formEl, msg);
  }
}

async function handleVote(type, id, action, button) {
  try {
    const url = button.dataset.url;
    const actionMap = { upvote: 1, downvote: -1 };
    const value = actionMap[action];
  
    if (button.classList.contains("active")) {
      action = "remove";
    }
  
    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken(),
      },
      body: JSON.stringify({ action }),
    });
  
    const data = await pJson(res);
  
    let activeAction = "";
    document.querySelectorAll(`.${type + id}-vote-btn`).forEach((btn) => {
      if (btn.classList.contains("active")) {
        activeAction = btn.dataset.action;
        btn.classList.remove("active");
      }
    });
    spanEl = document.getElementById(`${type + id}_vote_count`);
    let vote_count = parseInt(spanEl.innerHTML);
  
    if (action === "remove") {
      vote_count -= value;
    } else {
      button.classList.add("active");
      if (activeAction) {
        vote_count -= actionMap[activeAction];
      }
      vote_count += value;
    }
  
    spanEl.innerHTML = vote_count;
  } catch (err) {
    console.error(err);
    alert("Something went wrong, Please try again.");
  }
}

const handleCommentFormDisplay = (type, id, button) => {
  let btnType = button.dataset.btn;
  let commentForm = document.getElementById(`${type + id}_comment_form`);
  if (btnType === "show") {
    button.classList.add("at-hidden");
    commentForm.classList.remove("at-hidden");
  } else {
    commentForm.reset();
    commentForm.querySelector(`#${type + id}_comment_error`)?.remove();
    document
      .getElementById(`${type + id}_comment_btn`)
      .classList.remove("at-hidden");
    commentForm.classList.add("at-hidden");
  }
};

const addCommentToUi = (comment, type, id) => {
  const container = document.getElementById(`${type + id}_comments_container`);
  container.insertAdjacentHTML("beforeend", comment);
  formatUTCtoLocal(container);
};

const handleCommentSubmit = (e, type, id, form) => {
  e.preventDefault();
  let content = document.getElementById(`${type + id}_comment_content`).value;

  fetch(`${form.dataset.url}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCSRFToken(),
    },
    body: JSON.stringify({
      content: content.trim(),
      [type]: id,
    }),
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
      form.querySelector(`#${type + id}_comment_error`)?.remove();
      form.reset();
      addCommentToUi(data.html, type, id);
      document
        .getElementById(`${type + id}_comment_btn`)
        .classList.remove("at-hidden");
      form.classList.add("at-hidden");
    })
    .catch((err) => {
      const p = document.createElement("p");
      p.id = `${type + id}_comment_error`;
      p.className = "at-form-error mb-1";
      if (err.content) {
        p.textContent = err.content[0];
      } else {
        p.textContent = "some error occurred";
      }
      form.appendChild(p);
    });
};

const handleAcceptedAnswer = (id, button) => {
  let method,
    body = null;

  let questionSection = document.getElementById("question-section");
  let acceptedAnswer =
    questionSection.dataset.acceptedAnswerId !== ""
      ? parseInt(questionSection.dataset.acceptedAnswerId)
      : null;

  let url = questionSection.dataset.acceptUrl;

  if (acceptedAnswer === id) {
    method = "DELETE";
  } else {
    method = "POST";
    body = JSON.stringify({ answer: id });
  }

  fetch(url, {
    method,
    headers: {
      "X-CSRFToken": getCSRFToken(),
      ...(body && { "Content-Type": "application/json" }),
    },
    ...(body && { body }),
  })
    .then((res) =>
      res.ok
        ? res.json()
        : res.json().then((err) => {
            throw err;
          }),
    )
    .then((data) => {
      const prev = acceptedAnswer;
      acceptedAnswer = data.accepted_answer;
      questionSection.dataset.acceptedAnswerId =
        acceptedAnswer === null ? "" : `${acceptedAnswer}`;

      if (prev !== null && prev !== id) {
        updateAcceptedAnswerUI(prev, false);
      }

      updateAcceptedAnswerUI(id, acceptedAnswer === id);
    })
    .catch((err) => {
      console.error(err);
      alert("Something went wrong, Please try again.");
    });
};

function updateAcceptedAnswerUI(answerId, isAccepted) {
  const btn = document.getElementById(`answer${answerId}_acc_btn`);
  if (!btn) return;

  btn.dataset.accepted = isAccepted ? "True" : "False";
}

const fetchMoreComments = (type, id, button) => {
  const last_id = button.dataset.lastCommentId;
  const url = button.dataset.url;

  fetch(
    `${url}?${type === "question" ? "question_id" : "answer_id"}=${id}&last_id=${last_id}`,
    {
      method: "GET",
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
      data.comments.forEach((comment) =>
        addCommentToUi(comment.html, type, id),
      );
      button.dataset.lastCommentId = data.last_id;
      if (!data.has_more) {
        button.classList.add("at-hidden");
      }
    })
    .catch((err) => {
      console.error(err);
      alert("Something went wrong, Please try again.");
    });
};

document.addEventListener("click", (e) => {
  const voteBtn = e.target.closest("[data-vote]");
  if (voteBtn) {
    handleVote(
      voteBtn.dataset.type,
      voteBtn.dataset.id,
      voteBtn.dataset.action,
      voteBtn,
    );
  }

  const commentBtn = e.target.closest("[data-comment-form-display]");

  if (commentBtn) {
    handleCommentFormDisplay(
      commentBtn.dataset.type,
      commentBtn.dataset.id,
      commentBtn,
    );
  }

  const cancelCommentBtn = e.target.closest("[data-cancel-comment]");

  if (cancelCommentBtn) {
    handleCommentFormDisplay(
      cancelCommentBtn.dataset.type,
      cancelCommentBtn.dataset.id,
      cancelCommentBtn,
    );
  }

  const fetchCommentsBtn = e.target.closest("[data-fetch-comments]");

  if (fetchCommentsBtn) {
    fetchMoreComments(
      fetchCommentsBtn.dataset.type,
      fetchCommentsBtn.dataset.id,
      fetchCommentsBtn,
    );
  }

  const saveBtn = e.target.closest("[data-save]");

  if (saveBtn) {
    saveQuestion(saveBtn, saveBtn.dataset.id);
  }

  const acceptAnswerBtn = e.target.closest("[data-accept-answer]");

  if (acceptAnswerBtn) {
    handleAcceptedAnswer(parseInt(acceptAnswerBtn.dataset.id), acceptAnswerBtn);
  }
});

document.addEventListener("submit", (e) => {
  const commentForm = e.target.closest("[data-comment-form]");

  if (commentForm) {
    handleCommentSubmit(
      e,
      commentForm.dataset.type,
      commentForm.dataset.id,
      commentForm,
    );
  }

  const answerForm = e.target.closest("[data-answer-form]");

  if (answerForm) {
    handleAnswerSubmit(e);
  }
});
