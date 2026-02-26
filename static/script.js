async function loadTable() {
  const res = await fetch('/tournament/json');
  const data = await res.json();
  const tbody = document.querySelector('#tournament tbody');
  tbody.innerHTML = '';
  data.forEach(row => {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${row.players_name}</td>
      <td>${row.players_command}</td>
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
}

loadTable();
setInterval(loadTable, 5000); // обновление каждые 5 секунд

