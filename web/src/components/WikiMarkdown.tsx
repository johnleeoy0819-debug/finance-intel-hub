import { Link } from 'react-router-dom'

interface Props {
  content: string
}

export default function WikiMarkdown({ content }: Props) {
  // Pre-process wikilinks [[slug|text]] or [[slug]]
  const processed = content.replace(
    /\[\[([^\]|]+)(?:\|([^\]]+))?\]\]/g,
    (_, slug: string, displayText?: string) => {
      const cleanSlug = slug.trim().toLowerCase().replace(/\s+/g, '-').replace(/[^\w\-]/g, '')
      const text = displayText?.trim() || slug.trim()
      return `<WIKILINK slug="${cleanSlug}">${text}</WIKILINK>`
    }
  )

  // Split by wikilink placeholders and render
  const parts = processed.split(/(<WIKILINK slug="[^"]+">[^<]+<\/WIKILINK>)/)

  return (
    <div className="prose max-w-none text-gray-700 whitespace-pre-wrap leading-relaxed">
      {parts.map((part, i) => {
        const match = part.match(/<WIKILINK slug="([^"]+)">([^<]+)<\/WIKILINK>/)
        if (match) {
          return (
            <Link
              key={i}
              to={`/wiki/${match[1]}`}
              className="text-primary-600 hover:underline font-medium"
            >
              {match[2]}
            </Link>
          )
        }
        return <span key={i}>{part}</span>
      })}
    </div>
  )
}
