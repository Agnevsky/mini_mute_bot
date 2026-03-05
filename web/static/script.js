async function loadTable() {
  const res = await fetch('/tournament/json');
  const data = await res.json();
  
  data.sort((a, b) => {
    if (b.score !== a.score) return b.score - a.score;
    const a_reg = a.games_win - a.win_extra_time;
    const b_reg = b.games_win - b.win_extra_time;
    if (b_reg !== a_reg) return b_reg - a_reg;
    if (b.games_win !== a.games_win) return b.games_win - a.games_win;
    return b.different_goals - a.different_goals;
  });

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
setInterval(loadTable, 5000);
