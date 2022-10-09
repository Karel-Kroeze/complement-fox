<script lang="ts">
	import type { PageData } from './$types';
	import { formatDistanceToNow } from 'date-fns';
	import Recorder from '$lib/recorder.svelte';
	import type { MessageJSON } from '$lib/message';
	import type { Message, MessageData } from '$lib/server/message';

	export let data: PageData;

	const getMessageDetails = (msg: MessageData): string => {
		let details = `Created ${formatDistanceToNow(msg.createdAt, { addSuffix: true })}`;

		if (msg.receivedAt) {
			details += `\nReceived ${formatDistanceToNow(msg.receivedAt, { addSuffix: true })}`;
		} else {
			details += `\nNot yet received`;
		}

		if (msg.playedAt) {
			details += `\nPlayed ${formatDistanceToNow(msg.playedAt, { addSuffix: true })}`;
		} else {
			details += `\nNot yet played`;
		}

		return details;
	};

	const messageCreated = (msg: MessageJSON): void => {
		const hydrated_message = { ...msg, createdAt: new Date(msg.createdAt) };
		data.messages = [...data.messages, hydrated_message as any];
	};

	const discardMessage = async (msg: MessageData): Promise<void> => {
		data.messages = data.messages.filter((_msg) => _msg !== msg);
		const response = await fetch(`/message/${msg.id}/discard`);

		if (!response.ok) {
			const { headers, status } = response;
			console.error({ headers, body: await response.text(), status });
		}
	};
</script>

<div class="container">
	<h1>Messages</h1>
	{#each data.messages as message}
		<div class="message panel">
			<audio controls src={`messages/${message.id}.wav`} class="controls" />
			<div class="status" title={getMessageDetails(message)}>
				{#if message.receivedAt}
					<iconify-icon icon="mdi:check-all" class:played={message.playedAt} />
				{:else}
					<iconify-icon icon="mdi:check" />
				{/if}
			</div>
			<div on:click={() => discardMessage(message)} class="btn-secondary" title="discard message">
				<iconify-icon icon="mdi:trash-can" />
			</div>
		</div>
	{/each}

	<Recorder {messageCreated} />
</div>

<style lang="less">
	.message {
		& + .message {
			margin-top: 0.5em;
		}

		display: flex;
		flex-flow: row nowrap;
		align-items: center;
		justify-content: flex-start;

		gap: 1em;
	}

	.controls {
		margin-right: auto;
	}

	.status {
		font-size: 1.5em;
	}
</style>
