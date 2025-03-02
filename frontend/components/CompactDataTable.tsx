"use client"

import * as React from "react"
import { CompactTable } from "@table-library/react-table-library/compact"
import { useTheme, Theme } from "@table-library/react-table-library/theme"
import { darkTableStyles } from "@/components/tableTheme"

interface CompactDataTableProps {
  data: Record<string, any>[]
  title?: string
}

export function CompactDataTable({ data, title }: CompactDataTableProps) {
  if (!data || data.length === 0) {
    return <p>No data available.</p>
  }

  const nodes = React.useMemo(
    () => data.map((item, index) => ({ id: String(index), ...item })),
    [data]
  )

  const columns = React.useMemo(() => {
    const firstRow = data[0]
    return Object.keys(firstRow).map((key) => ({
      label: key,
      renderCell: (row: Record<string, any>) => {
        const cellValue = row[key]
        return typeof cellValue === "object"
          ? JSON.stringify(cellValue)
          : String(cellValue)
      },
    }))
  }, [data])

  const tableData = { nodes }

  // Convert the plain object to a theme
  const customTheme = useTheme(darkTableStyles)

  return (
    <div className="my-4">
      {title && <h3 className="mb-2 text-lg font-semibold">{title}</h3>}
      {/* Pass the custom theme via the theme prop */}
      <CompactTable columns={columns} data={tableData} theme={customTheme} />
    </div>
  )
}
