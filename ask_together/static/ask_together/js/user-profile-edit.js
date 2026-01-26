const profileImage = document.getElementById("profile_image");
const profileImgInput = document.getElementById("id_profile_image");
const clearImgChange = document.getElementById("clear_img_change");

function handleImageChange() {
  const file = profileImgInput.files?.[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = function (e) {
    profileImage.setAttribute("src", e.target.result);
    clearImgChange.classList.remove("at-hidden");
  };

  reader.readAsDataURL(file);
}

function resetImage(originalSrc) {
  profileImage.src = originalSrc;
  profileImgInput.value = "";
  clearImgChange.classList.add("at-hidden");
}

profileImgInput.addEventListener("change", handleImageChange);

document.addEventListener("click", (e) => {
  const clearImgBtn = e.target.closest("[data-clear-img]");

  if (clearImgBtn) {
    resetImage(clearImgBtn.dataset.imgSrc);
  }
});
