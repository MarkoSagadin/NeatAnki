const tagsContainer = document.querySelector(".tags");
if (tagsContainer) {
  let tags = tagsContainer.innerHTML.split(" ").filter(Boolean);
  tagsContainer.innerHTML = tags
    .map((tag) => {
      return `<div class='tag'>${tag.split("::").filter(Boolean).pop()}</div>`;
    })
    .join("");
}
