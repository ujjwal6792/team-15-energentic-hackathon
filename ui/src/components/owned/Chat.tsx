import { useState } from "react"
import { ChatContainer, ChatForm, ChatMessages } from "@/components/ui/chat"
import { MessageInput } from "@/components/ui/message-input"
import { MessageList } from "@/components/ui/message-list"
import { PromptSuggestions } from "../ui/prompt-suggestions"
import type { Message } from "../ui/chat-message"
import type { SessionResponse } from "@/store"

type Props = {
  session: SessionResponse
}

async function handleConversationStream(
  message: string,
  session: SessionResponse,
  onFinalMessage: (msg: Message) => void,
  onStreamUpdate: (partial: string) => void
) {
  const res = await fetch("https://solar-agent.dhiway.net/run_sse", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      app_name: session.app_name,
      user_id: session.user_id,
      session_id: session.id,
      new_message: {
        role: "user",
        parts: [{ text: message }]
      },
      streaming: true
    })
  });

  const reader = res.body?.getReader();
  const decoder = new TextDecoder("utf-8");

  let buffer = "";
  let accumulatedContent = "";

  while (reader) {
    const { value, done } = await reader.read();
    if (done) {
      if (accumulatedContent) {
        onFinalMessage({
          id: crypto.randomUUID(),
          role: "assistant",
          content: accumulatedContent.trim(),
          createdAt: new Date()
        });
      }
      break;
    }

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n\n");

    for (const chunk of lines) {
      if (!chunk.startsWith("data:")) continue;

      try {
        const json = JSON.parse(chunk.replace(/^data:\s*/, ""));
        const part = json?.content?.parts?.[0];
        const text = part?.text;

        if (text && json?.author === "tool_agent") {
          accumulatedContent += text;
          onStreamUpdate(accumulatedContent);
        }
      } catch (e) {
        console.warn("Error parsing chunk", chunk, e);
      }
    }

    buffer = "";
  }
}

const Chat = (props: Props) => {
  const { session } = props;

  const [inputField, setInputField] = useState("");
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [streamedText, setStreamedText] = useState("");

  const lastMessage = messages.at(-1);
  const isEmpty = messages.length === 0;
  const isTyping = lastMessage?.role === "user" && isLoading;

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!inputField.trim()) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: inputField,
      createdAt: new Date()
    };
    console.log('abc: ', userMessage)
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setStreamedText("");

    await handleConversationStream(
      inputField,
      session,
      (finalMsg) => {
        setMessages((prev) => [...prev, { ...finalMsg, content: finalMsg.content.split('\n')[0] }]);
        setStreamedText("");
        setIsLoading(false);
        setInputField("");
      },
      (partial) => setStreamedText(partial)
    );
  };

  const allMessages = streamedText
    ? [...messages, {
      id: "streaming",
      role: "assistant",
      content: streamedText,
      createdAt: new Date()
    }]
    : messages;

  return (
    <ChatContainer className="max-w-3xl grow">
      {!isEmpty && (
        <ChatMessages messages={allMessages}>
          <MessageList messages={allMessages} isTyping={isTyping} />
        </ChatMessages>
      )}

      <ChatForm className="mt-auto" isPending={isLoading || isTyping} handleSubmit={handleSubmit as any}>
        {() => (
          <MessageInput
            value={inputField}
            onChange={(e) => setInputField(e.target.value)}
            isGenerating={isLoading}
            stop={() => null}
          />
        )}
      </ChatForm>

      {/* <PromptSuggestions */}
      {/*   label="" */}
      {/*   append={(msg) => setMessages((prev) => [...prev, { ...msg, id: crypto.randomUUID() }])} */}
      {/*   suggestions={["subsidy?", "i want my status"]} */}
      {/* /> */}
    </ChatContainer>
  );
};

export default Chat;
