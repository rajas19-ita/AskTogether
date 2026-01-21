const profileImage = document.getElementById("profile_image");
const profileImgInput = document.getElementById("id_profile_image");
const clearImgChange = document.getElementById("clear_img_change");

profileImgInput.addEventListener("change", (e) => {
  const selectedFile = profileImgInput.files[0];
  const reader = new FileReader();

  reader.onload = function (e) {
    profileImage.setAttribute("src", e.target.result);
    clearImgChange.classList.remove("at-hidden");
  };
  reader.readAsDataURL(selectedFile);
});

const clearImg = (button) => {
  profileImage.src = button.dataset.imgSrc;

  profileImgInput.value = "";
  clearImgChange.classList.add("at-hidden");
};

document.addEventListener("click", (e) => {
  const clearImgBtn = e.target.closest("[data-clear-img]");

  if (clearImgBtn) {
    clearImg(clearImgBtn);
  }
});
