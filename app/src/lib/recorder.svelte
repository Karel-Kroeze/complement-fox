<script lang="ts">
	import { format } from 'date-fns';
	import timer from '$lib/timer';
	import '$lib/style.less';
	import type { MessageJSON } from './message';

	export let messageCreated: (msg: MessageJSON) => void;

	let mediaRecorder: MediaRecorder;
	let chunks: Blob[] = [];

	let messageBlob: Blob | undefined;
	let messageObjectUrl: string | undefined;

	let initialized = false;
	let allowed: boolean | undefined = undefined;
	let state = 'idle';
	let time_recording: number;
	let timer_unsubscribe: Function;

	const initializeStream = async () => {
		return await navigator.mediaDevices
			.getUserMedia({
				audio: true
			})

			// handle input stream
			.then((stream) => {
				mediaRecorder = new MediaRecorder(stream);
				mediaRecorder.ondataavailable = (event) => {
					chunks.push(event.data);
				};
				mediaRecorder.onstart = onStartRecording;
				mediaRecorder.onstop = onStopRecording;

				return true;
			})

			// handle errors
			.catch((err) => {
				console.error({ err });

				return false;
			});
	};

	const onStartRecording = () => {
		state = 'recording';
		timer_unsubscribe = timer.subscribe((time) => (time_recording = time));
	};

	const onStopRecording = async () => {
		state = 'idle';
		timer_unsubscribe?.();

		messageBlob = new Blob(chunks, { type: 'audio/webm' });
		messageObjectUrl = URL.createObjectURL(messageBlob);
		chunks = [];
	};

	const startRecording = async () => {
		if (!initialized) {
			allowed = await initializeStream();
		}
		if (!allowed) {
			console.log({ initialized, allowed });
		}

		mediaRecorder.start();
	};

	const stopRecording = () => {
		mediaRecorder.stop();
	};

	const discardRecording = () => {
		messageBlob = undefined;
		messageObjectUrl = undefined;
	};

	const createMessage = async () => {
		const message = await fetch('/message', { body: messageBlob, method: 'POST' }).then(
			(response) => response.json()
		);
		messageCreated(message);
		discardRecording();
	};
</script>

<h2>Record new message</h2>
<div class="panel recorder">
	{#if messageObjectUrl}
		<audio controls src={messageObjectUrl} />
		<div class="btn-secondary" on:click={createMessage} title="upload recording as new message">
			<iconify-icon icon="mdi:mail" />
		</div>
		<div class="btn-secondary" on:click={discardRecording} title="discard recording">
			<iconify-icon icon="mdi:trash-can" />
		</div>
	{:else}
		<div
			class="btn-secondary"
			disabled={state !== 'idle' || null}
			on:click={startRecording}
			title="start recording"
		>
			<iconify-icon inline icon="mdi:microphone" class:recording={state === 'recording'} />
		</div>
		{#if state === 'recording'}
			<div class="btn-secondary" on:click={stopRecording} title="stop recording">
				<iconify-icon inline icon="mdi:stop" />
			</div>
			<span class="time-recording"
				><iconify-icon icon="mdi:record" /> {format(time_recording, 'mm:ss')}</span
			>
		{/if}
	{/if}
</div>

<style lang="less">
	@import 'style.less';

	.recorder {
		display: flex;
		flex-flow: row wrap;
		align-items: center;
		justify-content: flex-start;
		gap: 1em;
	}

	.time-recording {
		background: @secondary-colour;
		border-radius: 1em;
		padding: 0.5em;
	}

	.recording {
		color: red;
	}

	.controls {
		display: flex;
		flex-flow: row nowrap;
		align-items: center;
		justify-content: flex-end;
		gap: 1em;
	}
</style>
