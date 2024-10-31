async function fetchStatus() {
  const response = await fetch("status");
  const status = await response.json();
  const table = document.getElementById("statusTable");
  table.innerHTML = "";

  for (const url in status) {
      var urlStatus = status[url]

      // Parse timestamp as UTC and adjust to local time
      const lastCheckedUtc = new Date(status[url].last_checked);

      // Define formatting options
      const timeOptions = { hour: 'numeric', minute: '2-digit' };
      const dateOptions = { day: 'numeric', month: 'short' };
      const fullDateOptions = { ...dateOptions, year: 'numeric', ...timeOptions };

      // Format time components
      const nowDateString = new Date().toLocaleDateString(undefined, dateOptions);
      const dateString = lastCheckedUtc.toLocaleDateString(undefined, dateOptions);
      const timeString = lastCheckedUtc.toLocaleTimeString(undefined, timeOptions);

      // Determine display format
      let localTimeString = dateString === nowDateString ? timeString : `${dateString}, ${timeString}`;


      const row = document.createElement("tr");
      row.style.backgroundColor = "#F5F5F5"
      row.style.color = "#555"

      if (urlStatus) {
          const statusCode = urlStatus.code
          if (statusCode > 199 & statusCode < 300) {
              row.style.backgroundColor = "#c7f1c7"
              row.style.color = "black"
          }
          else
          {
              row.style.backgroundColor = "#ffbbbb"
              row.style.color = "#410000"
              row.style.fontWeight = "700"
          }
      }
      row.innerHTML = `<td><a href="${url}" class="cell cell-content">${url}</a></td>
                       <td class="cell centre">${urlStatus.status ? "Up" : "Down"}</td>
                       <td class="cell centre">${urlStatus.code}</td>
                       <td class="cell centre">${localTimeString}</td>`;
      table.appendChild(row);
  }
}

setInterval(fetchStatus, 5000); // Refresh every 5 seconds
fetchStatus(); // Initial fetch