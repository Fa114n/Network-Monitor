function updateClock() {
  const now = new Date();
  document.getElementById('clock').textContent =
    now.toLocaleTimeString('en-GB');
}

async function fetchPing() {
  try {
    const res = await fetch('/api/ping');
    const data = await res.json();
    document.getElementById('ping-grid').innerHTML = data.map(host => `
      <div class="host-row ${host.alive ? 'alive' : 'dead'}">
        <div>
          <div class="host-name">${host.name}</div>
          <div class="host-ip">${host.host}</div>
        </div>
        <div class="host-badge">${host.alive ? '● ONLINE' : '● OFFLINE'}</div>
      </div>
    `).join('');
  } catch(e) { console.error(e); }
}

async function fetchStats() {
  try {
    const res = await fetch('/api/stats');
    const data = await res.json();
    const s = data.network;

    document.getElementById('bytes-sent').innerHTML = `${s.bytes_sent}<span class="stat-unit">MB</span>`;
    document.getElementById('bytes-recv').innerHTML = `${s.bytes_recv}<span class="stat-unit">MB</span>`;
    document.getElementById('pkts-sent').textContent = s.packets_sent.toLocaleString();
    document.getElementById('pkts-recv').textContent = s.packets_recv.toLocaleString();

    document.getElementById('interfaces-grid').innerHTML =
      data.interfaces.map(i => `
        <div class="iface-row">
          <div>
            <div class="iface-name">${i.name}</div>
            <div class="iface-ip">${i.ip}</div>
          </div>
          <span class="iface-badge ${i.is_up ? 'up' : 'down'}">
            ${i.is_up ? 'UP' : 'DOWN'}
          </span>
        </div>
      `).join('');

    document.getElementById('connections-body').innerHTML =
      data.connections.map(c => `
        <tr>
          <td>${c.local}</td>
          <td>${c.remote}</td>
          <td class="status-${c.status.toLowerCase()}">${c.status}</td>
          <td>${c.pid || '-'}</td>
        </tr>
      `).join('');
  } catch(e) { console.error(e); }
}

updateClock();
setInterval(updateClock, 1000);
fetchStats();
fetchPing();
setInterval(fetchStats, 5000);
setInterval(fetchPing, 10000);