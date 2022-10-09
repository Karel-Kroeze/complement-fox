import { sql } from '$lib/server/database';
import { Message } from '$lib/server/message';
import type { RequestHandler } from '@sveltejs/kit';

export const GET: RequestHandler = async ({ url }) => {
	console.log({ url });

	if (url.searchParams.get('sync')) {
		await sql.sync({ force: true });
	}

	if (!(url.searchParams.get('seed') === 'false')) {
		const message = await Message.create({});
		return new Response(JSON.stringify(message));
	} else {
		return new Response('OK');
	}
};

console.log({ sql });
