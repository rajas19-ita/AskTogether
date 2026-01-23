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

function setButtonsDisabled(buttons, disabled) {
  buttons.forEach((btn) => {
    btn.disabled = disabled;
  });
}

function applyVoteUI({ type, id, buttons, user_vote, score }) {
  buttons.forEach((btn) => {
    btn.classList.remove("active");
    if (user_vote === 1 && btn.dataset.action === "upvote") {
      btn.classList.add("active");
    } else if (user_vote === -1 && btn.dataset.action === "downvote") {
      btn.classList.add("active");
    }
  });

  const spanEl = document.getElementById(`${type + id}_vote_count`);
  spanEl.textContent = score;
}

async function handleVote(type, id, action, button) {
  const url = button.dataset.url;
  const voteBtnA = document.querySelectorAll(`.${type + id}-vote-btn`);

  try {
    setButtonsDisabled(voteBtnA, true);

    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken(),
      },
      body: JSON.stringify({ action }),
    });

    const data = await pJson(res);

    applyVoteUI({
      type,
      id,
      buttons: voteBtnA,
      user_vote: data.user_vote,
      score: data.upvotes - data.downvotes,
    });
  } catch (err) {
    console.error(err);
    notyfCenter.error("Something went wrong, Please try again.");
  } finally {
    setButtonsDisabled(voteBtnA, false);
  }
}

function removeCommentFormError(type, id, form) {
  form.querySelector(`#${type + id}_comment_error`)?.remove();
}

function commentFormHide(type, id, form) {
  form.reset();
  removeCommentFormError(type, id, form);
  document
    .getElementById(`${type + id}_comment_btn`)
    .classList.remove("at-hidden");
  form.classList.add("at-hidden");
}

function handleCommentFormDisplay(type, id, button) {
  let btnType = button.dataset.btn;
  let commentForm = document.getElementById(`${type + id}_comment_form`);
  if (btnType === "show") {
    button.classList.add("at-hidden");
    commentForm.classList.remove("at-hidden");
  } else {
    commentFormHide(type, id, commentForm);
  }
}

function addCommentToUi(comment, type, id) {
  const container = document.getElementById(`${type + id}_comments_container`);
  container.insertAdjacentHTML("beforeend", comment);
  formatUTCtoLocal(container);
}

function showCommentFormError(type, id, form, message) {
  removeCommentFormError(type, id, form);

  const p = document.createElement("p");
  p.id = `${type + id}_comment_error`;
  p.className = "at-form-error mb-1";
  p.textContent = message;
  form.appendChild(p);
}

async function handleCommentSubmit(e, type, id, form) {
  try {
    e.preventDefault();
    const url = form.dataset.url;
    const value = document.getElementById(`${type + id}_comment_content`).value;
    const comment = value?.trim() ?? "";

    if (!comment) {
      showCommentFormError(type, id, form, "Comment cannot be empty");
      return;
    }

    const res = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCSRFToken(),
      },
      body: JSON.stringify({
        content: comment,
        [type]: id,
      }),
    });

    const data = await pJson(res);

    addCommentToUi(data.html, type, id);
    commentFormHide(type, id, form);
  } catch (err) {
    const msg = err?.content?.[0] || "Some error occurred";
    showCommentFormError(type, id, form, msg);
  }
}

async function handleAcceptedAnswer(id, button) {
  try {
    let method,
      body = null;

    const questionSection = document.getElementById("question-section");
    let acceptedAnswer =
      questionSection.dataset.acceptedAnswerId !== ""
        ? parseInt(questionSection.dataset.acceptedAnswerId)
        : null;
    const url = questionSection.dataset.acceptUrl;

    if (acceptedAnswer === id) {
      method = "DELETE";
    } else {
      method = "POST";
      body = JSON.stringify({ answer: id });
    }

    const res = await fetch(url, {
      method,
      headers: {
        "X-CSRFToken": getCSRFToken(),
        ...(body && { "Content-Type": "application/json" }),
      },
      ...(body && { body }),
    });

    const data = await pJson(res);

    const prev = acceptedAnswer;
    acceptedAnswer = data.accepted_answer;
    questionSection.dataset.acceptedAnswerId =
      acceptedAnswer === null ? "" : `${acceptedAnswer}`;

    if (prev !== null && prev !== id) {
      updateAcceptedAnswerUI(prev, false);
    }

    updateAcceptedAnswerUI(id, acceptedAnswer === id);
  } catch (err) {
    console.error(err);
    notyfCenter.error("Something went wrong, Please try again.");
  }
}

function updateAcceptedAnswerUI(answerId, isAccepted) {
  const btn = document.getElementById(`answer${answerId}_acc_btn`);
  if (!btn) return;

  btn.dataset.accepted = isAccepted ? "True" : "False";
}

async function fetchMoreComments(type, id, button) {
  try {
    const last_id = button.dataset.lastCommentId;
    const url = button.dataset.url;

    const res = await fetch(
      `${url}?${type === "question" ? "question_id" : "answer_id"}=${id}&last_id=${last_id}`,
      {
        method: "GET",
        headers: {
          "X-CSRFToken": getCSRFToken(),
        },
      },
    );

    const data = await pJson(res);

    data.comments.forEach((comment) => addCommentToUi(comment.html, type, id));
    button.dataset.lastCommentId = data.last_id;
    if (!data.has_more) {
      button.classList.add("at-hidden");
    }
  } catch (err) {
    console.error(err);
    notyfCenter.error("Something went wrong, Please try again.");
  }
}

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
