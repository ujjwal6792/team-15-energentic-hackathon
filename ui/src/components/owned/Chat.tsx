import { useState } from "react"
import { ChatContainer, ChatForm, ChatMessages } from "@/components/ui/chat"
import { MessageInput } from "@/components/ui/message-input"
import { MessageList } from "@/components/ui/message-list"
/* import { PromptSuggestions } from "../ui/prompt-suggestions" */
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

  let accumulatedContent = "";
  let partialData = ""; // holds incomplete JSON between reads

  while (reader) {
    const { value, done } = await reader.read();
    if (done) break;

    // Add current decoded value to partial data
    partialData += decoder.decode(value, { stream: true });

    // Split based on double newline (end of event message)
    const segments = partialData.split("\n\n");

    // Keep the last part for next read in case it’s incomplete
    partialData = segments.pop() ?? "";

    for (const segment of segments) {
      if (!segment.trim().startsWith("data:")) continue;

      const jsonChunk = segment.replace(/^data:\s*/, "");

      try {
        const parsed = JSON.parse(jsonChunk);
        const part = parsed?.content?.parts?.[0];
        const text = part?.text;

        if (text && parsed?.author === "tool_agent") {
          accumulatedContent += text;
          onStreamUpdate(accumulatedContent);
        }
      } catch (err) {
        console.warn("Malformed JSON chunk skipped:", jsonChunk, err);
        // Could optionally store bad chunks or retry logic
      }
    }
  }

  if (accumulatedContent) {
    onFinalMessage({
      id: crypto.randomUUID(),
      role: "assistant",
      content: accumulatedContent.trim(),
      createdAt: new Date()
    });
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
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setStreamedText("");
    const input = inputField
    setInputField("");
    await handleConversationStream(
      input,
      session,
      (finalMsg) => {
        setMessages((prev) => [...prev, { ...finalMsg, content: finalMsg.content.split('\n')[0] }]);
        setStreamedText("");
        setIsLoading(false);
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
