async function loadTournament() {
    try {
        // Подставь сюда URL твоего API, который отдаёт JSON с турниром
        const response = await fetch("https://yourdomain.com/api/tournament");
        const data = await response.json();

        const tbody = document.querySelector("#tournament-table tbody");
        tbody.innerHTML = "";

        data.forEach(row => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>${row.players_command || "-"}</td>
                <td>${row.players_name || "-"}</td>
                <td>${row.games}</td>
                <td>${row.games_win}</td>
                <td>${row.games_lose}</td>
                <td>${row.score}</td>
                <td>${row.missed_goals}</td>
                <td>${row.score_goals}</td>
                <td>${row.different_goals}</td>
            `;
            tbody.appendChild(tr);
        });
    } catch (error) {
        console.error("Ошибка при загрузке таблицы:", error);
    }
}

// Загружаем таблицу при открытии страницы
loadTournament();

// Можно добавить авто-обновление каждые 10 секунд
setInterval(loadTournament, 10000);
