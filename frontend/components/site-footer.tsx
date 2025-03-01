import { Heart } from "lucide-react"

export function SiteFooter() {
  return (
    <footer className="border-t py-6 md:py-0">
      <div className="container flex flex-col items-center justify-between gap-4 md:h-16 md:flex-row">
        <p className="text-center text-sm leading-loose text-muted-foreground md:text-left">
          Built with <Heart className="inline-block h-4 w-4 text-red-500" /> by{" "}
          <a
            href="https://github.com/wnstnb"
            target="_blank"
            rel="noreferrer"
            className="font-medium underline underline-offset-4"
          >
            wnstnb
          </a>
        </p>
        <p className="text-center text-sm leading-loose text-muted-foreground md:text-right">
          Powered by Gemini 2.0 Flash API
        </p>
      </div>
    </footer>
  )
}

