
import { useEffect, useState } from "react"
import { ChatContainer, ChatForm, ChatMessages } from "@/components/ui/chat"
import { MessageInput } from "@/components/ui/message-input"
import { MessageList } from "@/components/ui/message-list"
import { PromptSuggestions } from "../ui/prompt-suggestions"
import type { Message } from "../ui/chat-message"
import axios from "axios"


async function HandleConversation(message: string) {
  console.log("message: ", message)
  const requestAgent = await axios.post("http://localhost:8000/run_sse", {
    app_name: "tool",
    new_message: { role: "user", parts: [{ text: message }] },
    session_id: "d5bf949a-f489-4870-b8bc-29a4ae21944b",
    streaming: false,
    user_id: "user",
  })
  const agentResponse = await requestAgent.data
  console.log(agentResponse)
  return agentResponse
}

const Chat = () => {
  const [inputField, setInputField] = useState('')
  const [messages, setMessages] = useState<Message[]>([{ role: 'assistant', content: "hello how can i help you?", id: '1' }])
  const [isLoading, _setIsLoading] = useState(false)
  const lastMessage = messages.at(-1)
  const isEmpty = messages.length === 0
  const isTyping = lastMessage?.role === "user" && isLoading

  /* useEffect(() => { */
  /*   _setIsLoading(true) */
  /*   setTimeout(() => { */
  /*     _setIsLoading(false) */
  /*   }, 2000) */
  /* }, [messages]) */

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
        handleSubmit={async (a) => {
          console.log('triggered')
          a?.preventDefault && a.preventDefault()
          await HandleConversation(inputField)
        }
        }
      >
        {() => (
          <MessageInput
            value={inputField}
            onChange={(a) => setInputField(a.target.value)}
            /* files={files} */
            /* setFiles={setFiles} */
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


/* const a = (a) => { a?.preventDefault && a?.preventDefault(); setMessages(e => [...e, ({ role: 'user', id: 'ac', content: inputField })]), setInputField('') } */
