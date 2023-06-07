document.addEventListener('DOMContentLoaded', () => {
    const closePopup = document.querySelector(".popup-close");
    const openPopup = document.querySelector(".change-password-link")
    const popup = document.querySelector(".popup");

    closePopup.addEventListener("click", () => {
        popup.style.visibility = "hidden";
        popup.style.opacity = 0;
    })

    openPopup.addEventListener("click", () => {
        popup.style.visibility = "visible";
        popup.style.opacity = 1;
    })
})