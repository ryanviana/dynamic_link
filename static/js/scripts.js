// Function to copy URL to clipboard
document.addEventListener("DOMContentLoaded", function () {
  const copyButtons = document.querySelectorAll(".copy-button");

  copyButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      const url = this.getAttribute("data-url");
      navigator.clipboard
        .writeText(url)
        .then(() => {
          alert("Shortened URL copied to clipboard.");
        })
        .catch((err) => {
          console.error("Could not copy text: ", err);
        });
    });
  });
});
