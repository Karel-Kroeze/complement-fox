import type { MessageData } from './server/message';

export type ModelJSON<T> = {
	[K in keyof T]: T[K] extends Date ? string : T[K];
};

export type MessageJSON = ModelJSON<MessageData>;
