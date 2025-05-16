interface PromptSuggestionsProps {
  label: string
  append: (message: { role: "user"; content: string }) => void
  suggestions: string[]
}

export function PromptSuggestions({
  label,
  append,
  suggestions,
}: PromptSuggestionsProps) {
  return (
    <div className="space-y-3">
      <h2 className="text-left text text-[#4c4f69]">{label}</h2>
      <div className="flex px-4 flex-wrap gap-6 text-sm">
        {suggestions.map((suggestion) => (
          <button
            key={suggestion}
            onClick={() => append({ role: "user", content: suggestion })}
            className="h-min flex-1 rounded-xl min-w-64 shadow bg-[#B6DDF6] text-indigo-900 cursor-pointer px-4 py-3 hover:bg-[#B6DDF675]"
          >
            <p>{suggestion}</p>
          </button>
        ))}
      </div>
    </div>
  )
}
