import { Message } from '$lib/server/message';
import type { RequestHandler } from '@sveltejs/kit';
import { Op } from 'sequelize';

export const GET: RequestHandler = async () => {
	const messages = await Message.findAll({ where: { receivedAt: { [Op.is]: undefined } } });

	return new Response(messages.map((msg) => msg.id).join('\n'));
};
