export function exportToCsv(filename: string, rows: any[]) {
  if (!rows || rows.length === 0) return;

  // Get columns from keys of the first object
  const columns = Object.keys(rows[0]);
  const csvRows = [];

  // Add header row
  csvRows.push(columns.join(","));

  // Add data rows
  for (const row of rows) {
    const values = columns.map(col => {
      // Escape double quotes in values and wrap in double quotes
      const escaped = (row[col] || "").toString().replace(/"/g, '""');
      return `"${escaped}"`;
    });
    csvRows.push(values.join(","));
  }

  const csvString = csvRows.join("\n");
  const blob = new Blob([csvString], { type: "text/csv" });
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.setAttribute("hidden", "");
  a.setAttribute("href", url);
  a.setAttribute("download", filename);
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
}
