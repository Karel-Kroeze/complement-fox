import { Message } from '$lib/server/message';
import { invalid, redirect } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';

export const load: PageServerLoad = async () => {
	const messages = await (await Message.findAll()).map((msg) => msg.toJSON());

	return { messages };
};
