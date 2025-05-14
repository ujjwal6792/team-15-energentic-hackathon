/* import { Button } from "./components/ui/button" */
import { useState } from "react"
import { Chat } from "./components/ui/chat"
import type { Message } from "./components/ui/chat-message"

function App() {
  const [inputField, setInputField] = useState('')
  const [messages, setMessages] = useState<Message[]>([{ role: 'assistant', content: "hello how can i help you?", id: '1' }])
  return (
    <div className="mx-auto w-svw max-w-5xl px-4 h-svh flex justify-center items-center">
      {/* <Button className="cursor-pointer" variant="secondary">Let's get started</Button> */}
      <Chat
        className="grow"
        messages={messages}
        handleSubmit={(a) => { a?.preventDefault && a?.preventDefault(); setMessages(e => [...e, ({ role: 'user', id: 'ac', content: inputField })]) }}
        input={inputField}
        handleInputChange={(a) => setInputField(a.target.value)}
        isGenerating={false}
        stop={stop}
        append={() => { }}
        setMessages={(message) => setMessages(message)}
        suggestions={[
          "What is the weather in San Francisco?",
          "Explain step-by-step how to solve this math problem: If x² + 6x + 9 = 25, what is x?",
          "Design a simple algorithm to find the longest palindrome in a string.",
        ]}
      />
    </div>
  )
}

export default App


