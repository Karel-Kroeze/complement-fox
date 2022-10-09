<script lang="ts">
	import 'iconify-icon';
	import '$lib/style.less';
</script>

<div class="container">
	<slot />
</div>

<style lang="less">
	:global body {
		background: #eee;
		font-family: Roboto, sans-serif;
	}

	.container {
		max-width: min(800px, 90vw);
		margin: 0 auto;
	}

	:global .btn {
		display: block;
		width: max-content;
		margin: 2em auto;
		padding: 0.8em 1.6em;
		box-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
		border-radius: 0.2em;

		text-transform: uppercase;
		text-decoration: none;
		font-size: larger;
		color: #fff;
		background-color: rgb(44, 44, 173);
	}
</style>
