import { writable } from "svelte/store";

export interface IHistory {
    text: string;
    audio: AudioBuffer;
}
export const history = writable([]);
export const appendToHistory = (element: IHistory) => {
    history.update((current) => [...current, element]);
};
