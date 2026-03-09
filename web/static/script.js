async function loadData() {
  const res = await fetch('/tournament/json');
  const data = await res.json();

  data.sort((a, b) => {
    if (b.score !== a.score) return b.score - a.score;
    const a_reg = a.games_win - (a.win_extra_time || 0);
    const b_reg = b.games_win - (b.win_extra_time || 0);
    if (b_reg !== a_reg) return b_reg - a_reg;
    if (b.games_win !== a.games_win) return b.games_win - a.games_win;
    return b.different_goals - a.different_goals;
  });

  // === ГЛАВНАЯ ===
  const tbody = document.querySelector('#tournament tbody');
  if (tbody) {
    tbody.innerHTML = '';
    data.forEach((row, i) => {
      const tr = document.createElement('tr');
      const diff = row.different_goals > 0 ? '+' + row.different_goals : row.different_goals;
      tr.innerHTML = `
        <td>${i + 1}</td>
        <td style="text-align:left">${row.players_name}</td>
        <td>${row.players_command || '—'}</td>
        <td>${row.games}</td>
        <td>${row.games_win}</td>
        <td>${row.games_lose}</td>
        <td class="score-bold">${row.score}</td>
        <td>${row.score_goals}</td>
        <td>${row.missed_goals}</td>
        <td>${diff}</td>
      `;
      tbody.appendChild(tr);
    });
  }

// === РЕЗУЛЬТАТЫ ИГР ===
const resultsRes = await fetch('/results/json');
const resultsData = await resultsRes.json();

const resultsList = document.getElementById('results-list');
if (resultsList) {
    resultsList.innerHTML = '';
    
    if (resultsData.length === 0) {
        resultsList.innerHTML = '<p style="text-align:center; color:#888">Игры ещё не сыграны</p>';
    } else {
        resultsData.forEach((r, i) => {
            const div = document.createElement('div');
            div.className = 'result-item';
            const extra = r.extra_time ? '<span class="result-badge">ОТ</span>' : '';
            const team1 = r.team1 ? ` <span class="result-team">(${r.team1})</span>` : '';
            const team2 = r.team2 ? ` <span class="result-team">(${r.team2})</span>` : '';
            div.innerHTML = `
                <span class="result-num">${i + 1}</span>
                <span class="result-player">${r.player1}${team1}</span>
                <span class="result-score">${r.score1} : ${r.score2}${extra}</span>
                <span class="result-player right">${r.player2}${team2}</span>
            `;
            resultsList.appendChild(div);
        });
    }
}

  // === СТАТИСТИКА ===
  const statsGrid = document.getElementById('stats-grid');
  if (statsGrid && data.length > 0) {
    const topScore = [...data].sort((a,b) => b.score - a.score)[0];
    const topGoals = [...data].sort((a,b) => b.score_goals - a.score_goals)[0];
    const topWins  = [...data].sort((a,b) => b.games_win - a.games_win)[0];
    const topDiff  = [...data].sort((a,b) => b.different_goals - a.different_goals)[0];

    statsGrid.innerHTML = `
      <div class="stat-card">
        <div class="stat-label">Лидер по очкам</div>
        <div class="stat-name">${topScore.players_name}</div>
        <div class="stat-value">${topScore.score}</div>
        <div class="stat-sub">очков</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Лучший бомбардир</div>
        <div class="stat-name">${topGoals.players_name}</div>
        <div class="stat-value">${topGoals.score_goals}</div>
        <div class="stat-sub">голов забито</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Больше всех побед</div>
        <div class="stat-name">${topWins.players_name}</div>
        <div class="stat-value">${topWins.games_win}</div>
        <div class="stat-sub">побед</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Лучшая разница</div>
        <div class="stat-name">${topDiff.players_name}</div>
        <div class="stat-value">+${topDiff.different_goals}</div>
        <div class="stat-sub">разница голов</div>
      </div>
    `;
  }
}

function switchTab(name, el) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
  el.classList.add('active');
  document.getElementById('panel-' + name).classList.add('active');
}

loadData();
setInterval(loadData, 5000);