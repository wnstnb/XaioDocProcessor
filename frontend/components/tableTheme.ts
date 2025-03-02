// tableTheme.ts
import { Theme } from "@table-library/react-table-library/theme"
// import { CompactTable } from "@table-library/react-table-library/compact"

export const darkTableStyles: Theme = {
    BaseRow: `
        background-color: #141414;
      `,
    Table: `
      --data-table-library_grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
      font-family: Consolas;
      font-size: 9pt;
      background-color: #1f1f1f;
      color: #f5f5f5;
      border-radius: 0.25rem;
      border: 1px solid #2e2e2e;
    `,
    HeaderRow: `
      background-color: #2b2b2b;
      color: #fff;
      border-bottom: 1px solid #444;
    `,
    Row: `
      border-bottom: 1px solid #2e2e2e;
      &:hover {
        background-color: #2f2f2f !important; /* Force a dark hover color */
      }
    `,
    HeaderCell: `
      padding: 0.25rem;
      text-align: left;
    `,
    Cell: `
      padding: 0.25rem;
    `,
  }