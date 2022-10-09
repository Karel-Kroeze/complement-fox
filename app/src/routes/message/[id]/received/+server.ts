import { Message } from '$lib/server/message';
import type { RequestHandler } from '@sveltejs/kit';

export const GET: RequestHandler = async ({ params }) => {
	const message = await Message.findByPk(params.id);

	if (!message) {
		return new Response('MESSAGE NOT FOUND', { status: 400 });
	}

	if (message.receivedAt) {
		return new Response('MESSAGE ALREADY RECEIVED', { status: 400 });
	}

	message.receivedAt = new Date();
	await message.save();

	return new Response(JSON.stringify(message.toJSON()));
};
