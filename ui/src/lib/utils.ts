import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export interface Attachment {}
export interface ToolInvocation {}
export interface MessagePart {
  text: string;
}

export interface Message {
  id: string;
  role: 'user' | 'assistant' | (string & {});
  content: string;
  createdAt?: Date;
  experimental_attachments?: Attachment[];
  toolInvocations?: ToolInvocation[];
  parts?: MessagePart[];
}

export function convertToMessage(response: any): Message {
  console.log('Response: ', response);
  return {
    id: response.id,
    role: response.content?.parts?.length > 0 ? 'assistant' : 'user',
    content:
      response.content?.parts?.map((part: any) => part.text).join('\n') || '',
    createdAt: response.timestamp
      ? new Date(response.timestamp * 1000)
      : undefined,
    parts: response.content?.parts || [],
    // Optional fields based on availability
    experimental_attachments: response.experimental_attachments ?? [],
    toolInvocations: response.toolInvocations ?? [],
  };
}
