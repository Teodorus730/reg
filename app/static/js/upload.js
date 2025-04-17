document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("trackModal");
    const openModalBtn = document.getElementById("openModal");
    const closeModalBtn = document.getElementById("closeModal");
    const form = document.getElementById("trackForm");
    const trackList = document.getElementById("trackList");

    openModalBtn.addEventListener("click", () => {
        modal.style.display = "flex";
    });

    closeModalBtn.addEventListener("click", () => {
        modal.style.display = "none";
    });

    window.addEventListener("click", event => {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });

    // Отправка формы трека через AJAX
    form.addEventListener("submit", async function (e) {
        e.preventDefault();
        const formData = new FormData(form);
        const response = await fetch("/upload/add_track", {
            method: "POST",
            body: formData
        });
        const result = await response.json();
        if (result.status === "success") {
            const track = result.track;
            const li = document.createElement("li");
            li.textContent = `${track.title} - ${track.artists}`;
            trackList.appendChild(li);
            modal.style.display = "none";
            form.reset();
        } else {
            alert("Ошибка добавления трека");
        }
    });
});
