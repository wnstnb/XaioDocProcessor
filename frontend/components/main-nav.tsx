"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { cn } from "@/lib/utils"
import { FileText, BarChart2, MessageSquare, Home } from "lucide-react"

const items = [
  {
    title: "Overview",
    href: "/",
    icon: <Home className="mr-2 h-4 w-4" />,
  },
  {
    title: "Documents",
    href: "/documents",
    icon: <FileText className="mr-2 h-4 w-4" />,
  },
  {
    title: "ChatDB",
    href: "/chat",
    icon: <MessageSquare className="mr-2 h-4 w-4" />,
  },
]

export function MainNav() {
  const pathname = usePathname()

  return (
    <div className="mr-4 flex">
      <Link href="/" className="mr-6 flex items-center space-x-2">
      <img src="/xaiodocpro_hexa_big.png" height="24" width="24" alt="Xaio"></img>
        <span className="hidden font-bold sm:inline-block">Xaio</span>
      </Link>
      <nav className="flex items-center space-x-6 text-sm font-medium">
        {items.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={cn(
              "flex items-center text-sm font-medium transition-colors hover:text-primary",
              pathname === item.href ? "text-foreground" : "text-muted-foreground",
            )}
          >
            {item.icon}
            {item.title}
          </Link>
        ))}
      </nav>
    </div>
  )
}

