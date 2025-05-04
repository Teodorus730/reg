let trackCount = 0;

function showTab(tabName) {
    document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));

    document.getElementById(`${tabName}-tab`).classList.add('active');
    document.getElementById(`${tabName}-content`).classList.add('active');
}

function toggleTrackBody(id) {
    const body = document.getElementById(`track-body-${id}`);
    const button = document.getElementById(`toggle-button-${id}`);
    if (body && button) {
        body.classList.toggle('active');
        const isActive = body.classList.contains('active');
        button.textContent = isActive ? 'Свернуть' : 'Развернуть';
    }
}

function removeTrack(id) {
    const el = document.getElementById(`track-${id}`);
    if (el) el.remove();
}

function updateTrackTitle(index) {
    const input = document.querySelector(`[name="tracks-${index}-title"]`);
    const header = document.getElementById(`track-title-${index}`);
    if (input && header) {
        const title = input.value.trim();
        header.textContent = title || "Новый трек";
    }
}

function addTrack() {
    const container = document.getElementById("tracks");
    let template = document.getElementById("track-template").innerHTML;
    template = template.replace(/__prefix__/g, trackCount);

    const div = document.createElement("div");
    div.id = `track-${trackCount}`;
    div.innerHTML = template;
    container.appendChild(div);

    const input = div.querySelector(`[name="tracks-${trackCount}-title"]`);
    if (input) {
        input.addEventListener('input', () => updateTrackTitle(trackCount));
    }

    trackCount++;
}

window.addEventListener("DOMContentLoaded", () => {
    addTrack();  // Добавить один трек по умолчанию
});


function previewCover(event) {
    const file = event.target.files[0];
    const preview = document.getElementById("cover-preview");
    if (file && preview) {
        const reader = new FileReader();
        reader.onload = e => {
            preview.src = e.target.result;
        };
        reader.readAsDataURL(file);
    }
}
