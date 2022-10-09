import { readable } from 'svelte/store';

const timer = readable(0, (set) => {
	const start = Date.now();
	const interval = setInterval(() => {
		const now = Date.now();
		set(now - start);
	}, 10);

	return () => {
		clearInterval(interval);
	};
});

export default timer;
