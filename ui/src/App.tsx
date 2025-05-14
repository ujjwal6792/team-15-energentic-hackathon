/* import { Button } from "./components/ui/button" */
import { useState } from "react"
/* import { Chat } from "./components/ui/chat" */
import type { Message } from "./components/ui/chat-message"
import { ChatContainer, ChatForm, ChatMessages } from "@/components/ui/chat"
import { MessageInput } from "@/components/ui/message-input"
import { MessageList } from "@/components/ui/message-list"
import { PromptSuggestions } from "./components/ui/prompt-suggestions"

function App() {
  const [inputField, setInputField] = useState('')
  const [messages, setMessages] = useState<Message[]>([{ role: 'assistant', content: "hello how can i help you?", id: '1' }])
  const [isLoading, _setIsLoading] = useState(false)
  const lastMessage = messages.at(-1)
  const isEmpty = messages.length === 0
  const isTyping = lastMessage?.role === "user"
  return (
    <div className="mx-auto w-svw max-w-5xl px-4 h-svh flex justify-center items-end">
      <ChatContainer className="max-w-3xl grow">
        {/* {isEmpty ? ( */}
        {/* ) : null} */}

        {!isEmpty ? (
          <ChatMessages messages={messages}>
            <MessageList messages={messages} isTyping={isTyping} />
          </ChatMessages>
        ) : null}

        <ChatForm
          className="mt-auto"
          isPending={isLoading || isTyping}
          handleSubmit={(a) => { a?.preventDefault && a?.preventDefault(); setMessages(e => [...e, ({ role: 'user', id: 'ac', content: inputField })]), setInputField('') }}
        >
          {({ files, setFiles }) => (
            <MessageInput
              value={inputField}
              onChange={(a) => setInputField(a.target.value)}
              /* allowAttachments */
              files={files}
              setFiles={setFiles}
              stop={stop}
              isGenerating={isLoading}
            />
          )}
        </ChatForm>
        <PromptSuggestions
          label=""
          append={(a) => setMessages(e => [...e, { ...a, id: '' }])}
          suggestions={["subsidy?", "i want my status"]}
        />
      </ChatContainer>
      {/* <Button className="cursor-pointer" variant="secondary">Let's get started</Button> */}
      {/* <Chat
        className="grow"
        messages={messages}
        handleSubmit={(a) => { a?.preventDefault && a?.preventDefault(); setMessages(e => [...e, ({ role: 'user', id: 'ac', content: inputField })]) }}
        input={inputField}
        handleInputChange={(a) => setInputField(a.target.value)}
        isGenerating={false}
        stop={() => { }}
        append={() => { }}
        setMessages={(message) => setMessages(message)}
        suggestions={[
          "What is the weather in San Francisco?",
          "Explain step-by-step how to solve this math problem: If x² + 6x + 9 = 25, what is x?",
          "Design a simple algorithm to find the longest palindrome in a string.",
        ]}
      /> */}

    </div>
  )
}

export default App


