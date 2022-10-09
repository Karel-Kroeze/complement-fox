import type { RequestHandler } from './$types';
import { Message } from '$lib/server/message';
import fs from 'fs/promises';

const tryDiscard = async (id: string, extensions = ['wav', 'weba']) => {
	for (const ext of extensions) {
		const path = `static/messages/${id}.${ext}`;

		try {
			await fs.unlink(path);
		} catch (err) {
			console.error(`failed to discard '${path}': ${err}`);
		}
	}
};

export const GET: RequestHandler = async ({ request, params }) => {
	const message = await Message.findByPk(params.id);

	if (!message) {
		return new Response('MESSAGE NOT FOUND', { status: 404 });
	}

	await message.destroy();
	await tryDiscard(message.id);

	return new Response('OK');
};
