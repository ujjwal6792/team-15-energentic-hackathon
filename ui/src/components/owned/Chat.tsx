
import { useState } from "react"
import { ChatContainer, ChatForm, ChatMessages } from "@/components/ui/chat"
import { MessageInput } from "@/components/ui/message-input"
import { MessageList } from "@/components/ui/message-list"
import { PromptSuggestions } from "../ui/prompt-suggestions"
import type { Message } from "../ui/chat-message"

const Chat = () => {
  const [inputField, setInputField] = useState('')
  const [messages, setMessages] = useState<Message[]>([{ role: 'assistant', content: "hello how can i help you?", id: '1' }])
  const [isLoading, _setIsLoading] = useState(false)
  const lastMessage = messages.at(-1)
  const isEmpty = messages.length === 0
  const isTyping = lastMessage?.role === "user"

  return (
    <ChatContainer className="max-w-3xl grow">
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
  )
}

export default Chat
