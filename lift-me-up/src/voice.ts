import { writable } from "svelte/store";

export interface IVoice {
    name?: string;
    languageCode: string;
    gender?: string;
}

export const voice = writable<IVoice>({
    name: "en-AU-Neural2-B",
    languageCode: "en-AU",
});
