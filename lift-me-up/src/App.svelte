<script lang="ts">
    import { onMount } from "svelte";
    import { history, appendToHistory, type IHistory } from "./history";
    import { voice, type IVoice } from "./voice";
    import { createNoise3D } from "simplex-noise";
    import Color from "color";
    import loading_messages from "./assets/loading_messages";

    const base_url = "http://fox.home.karel-kroeze.nl";
    const super_secret_key = "aduGwVzZ2i93DWxaPqbEi6QcRdzZdD3s5djC3CnGmo8p"; // capped at a low cost, but TODO: use a secure gatekeeper

    let text: string;
    let canvas: HTMLCanvasElement;
    let selected_history: IHistory;
    let languageCode: string = $voice.languageCode;
    let voices: { [languageCode: string]: IVoice[] } = {
        [$voice.languageCode]: [$voice],
    };
    let loading = false;
    let loading_message: string;

    // random element helper
    const random = (array) => {
        return array[Math.floor(Math.random() * array.length)];
    };

    // get and massage list of voices
    const getVoices = async () => {
        const url = new URL("voices", base_url);
        const _voices = await fetch(url).then((res) => {
            if (!res.ok) {
                console.error("failed fetching voices:", {
                    statusCode: res.status,
                    statustText: res.statusText,
                });
                return;
            }

            return res.json();
        });

        const __voices = {};
        for (let lang in _voices) {
            if (!__voices[lang]) {
                __voices[lang] = [];
            }
            for (let _voice of _voices[lang]) {
                __voices[lang].push({
                    languageCode: lang,
                    gender: _voice.ssmlGender,
                    name: _voice.name,
                });
            }
        }

        voices = __voices;
    };

    // set up audio context
    const context = new AudioContext();

    // visualization
    const analyzer = context.createAnalyser();
    analyzer.connect(context.destination);
    analyzer.smoothingTimeConstant = 0.95;

    // buffer for fft values
    let viz_columns: number;
    let analyzer_buffer: Uint8Array;

    const colour_a = Color("#ee964b");
    const colour_b = Color("#f95738");

    const initVisualization = () => {
        // set canvas draw area to same size as actual client area
        canvas.width = canvas.clientWidth;
        canvas.height = canvas.clientHeight;

        // pick reasonable cell size for visualization
        let cell_count = 2;
        let cell_size = Math.ceil(canvas.width / cell_count);

        while (cell_size > 64) {
            cell_count *= 2;
            cell_size = Math.ceil(canvas.width / cell_count);
        }

        console.log({ cell_size, cell_count });

        viz_columns = cell_count;
        analyzer.fftSize = cell_count * 8; // fft goes up to really high freqs, we only need the lower half or so
        analyzer_buffer = new Uint8Array(cell_count * 2);
    };

    const replayComplement = async (ev: SubmitEvent) => {
        ev.preventDefault();

        // check if audio context was suspended
        if (context.state === "suspended") {
            await context.resume();
        }

        const source = new AudioBufferSourceNode(context, {
            buffer: selected_history.audio,
        });
        source.connect(analyzer);
        source.start(0);
    };

    const playComplement = async (ev: SubmitEvent) => {
        // cancel form event
        ev.preventDefault();

        // check if audio context was suspended
        if (context.state === "suspended") {
            await context.resume();
        }

        loading = true;
        const url = new URL("complement", base_url);
        url.searchParams.set("q", text);
        url.searchParams.set("key", super_secret_key);
        url.searchParams.set("voice", $voice.name);

        const raw_audio = await fetch(url).then((response) => {
            if (!response.ok) {
                const { status, statusText: label } = response;
                console.log("error fetching complement", { status, label });
            }
            return response.arrayBuffer();
        });
        loading = false;

        if (!raw_audio) {
            return;
        }
        const buffer = await context.decodeAudioData(raw_audio);
        const source = new AudioBufferSourceNode(context, { buffer });
        source.connect(analyzer);
        source.start(0);

        // while that is happening, also add to the history
        appendToHistory({ text: `${text} (${$voice.name})`, audio: buffer });
    };

    let viz;
    let t = 0;
    const noise = createNoise3D();
    const updateVisualization = async () => {
        viz = requestAnimationFrame(updateVisualization);
        if (!canvas) {
            return;
        }

        const ctx = canvas.getContext("2d");
        analyzer.getByteFrequencyData(analyzer_buffer);

        const columns = viz_columns;
        const size = Math.ceil(canvas.width / columns);
        const rows = Math.floor(canvas.height / size);
        const cell_fill = 0.6; // proportion of filled cell
        const cell_flow = 0.05; // proportion of empty space for random movement

        // attempt to offset canvas to keep viz in bottom-center
        ctx.resetTransform();
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.translate(
            (canvas.width - columns * size) / 2,
            canvas.height - rows * size
        );
        ctx.shadowBlur = size / 5;
        ctx.shadowColor = Color("#000000cc").hex();
        ctx.shadowOffsetX = size / 20;
        ctx.shadowOffsetY = size / 20;

        for (let col = 0; col < columns; col++) {
            let column_value = analyzer_buffer[col] * (rows / 2 ** 8);
            let row = 0;
            while (row < rows && column_value > 0.5) {
                const value = Math.min(column_value, 1.0);

                const x =
                    (col + 0.5) * size +
                    noise(col * 0.1, row * 0.1, t) *
                        size *
                        (1 - cell_fill) *
                        cell_flow;
                const y =
                    canvas.height -
                    (row + 0.5) * size +
                    noise(col * 0.1 + 50, row * 0.1 + 50, t) *
                        size *
                        (1 - cell_fill) *
                        cell_flow;

                const _size = value * size * cell_fill; // don't want to fill the whole screen;
                const _offset = _size / 2;

                ctx.fillStyle = colour_a
                    .mix(
                        colour_b,
                        column_value / 5 / 2 + noise(col, row, t * 2) / 2 + 0.5
                    )
                    .hex();
                ctx.fillRect(x - _offset, y - _offset, _size, _size);

                row += 1;
                column_value -= 1;
            }
        }

        t += 0.01;
    };

    onMount(() => {
        initVisualization();
        updateVisualization();
        getVoices();

        // continuous update loading message, even when not needed...
        setInterval(() => {
            loading_message = random(loading_messages);
        }, 800);
    });
</script>

<header />
<main class="container">
    <h1 class="title">Lift me up!</h1>

    <section class="widget">
        <form action="" on:submit={playComplement}>
            <div class="field">
                <label for="subject">
                    What are you feeling insecure about?
                </label>
                <input
                    type="text"
                    id="subject"
                    bind:value={text}
                    disabled={loading ? true : null}
                />
                <label
                    for="voice"
                    style="margin-top: 1em; display: inline-block;"
                >
                    What soothing voice should I use?
                </label>
                <div class="flex">
                    <select
                        name="language"
                        id="language"
                        bind:value={languageCode}
                        disabled={loading ? true : null}
                    >
                        {#each Object.keys(voices)
                            .sort()
                            .filter((lang) => lang.startsWith("en")) as lang}
                            <option>{lang}</option>
                        {/each}
                    </select>
                    <select
                        name="voice"
                        id="voice"
                        bind:value={$voice}
                        disabled={loading ? true : null}
                    >
                        {#if languageCode}
                            {#each voices[languageCode] as voice}
                                <option value={voice}
                                    >{voice.gender === "MALE" ? "♂" : "♀"}
                                    {voice.name}</option
                                >
                            {/each}
                        {/if}
                    </select>
                </div>
                <button type="submit" disabled={loading ? true : null}>
                    {#if loading}
                        {loading_message}
                    {:else}
                        Lift me up!
                    {/if}
                </button>
            </div>
        </form>
    </section>

    {#if $history.length > 0}
        <section class="widget history">
            <form action="" on:submit={replayComplement}>
                <div class="field">
                    <label for="history">Or play a previous message</label>
                    <select
                        name="history"
                        id="history"
                        bind:value={selected_history}
                    >
                        {#each $history as hist}
                            <option value={hist}>{hist.text}</option>
                        {/each}
                    </select>
                    <button type="submit"> Say it again! </button>
                </div>
            </form>
        </section>
    {/if}
</main>
<canvas id="viz" bind:this={canvas} on:resize={initVisualization} />

<svelte:window on:resize={initVisualization} />

<style lang="scss">
    @use "colours" as *;
    @use "sass:color";

    #viz {
        margin-top: 1em;
        display: flex;
        // border: 1px solid $tertiary;

        width: 100%;
        height: calc(max(80vh, 240px));

        position: absolute;
        left: 0;
        bottom: 0;
        right: 0;

        pointer-events: none;

        z-index: 1;
    }

    .flex {
        display: flex;
        gap: 0.5em;
    }

    .container {
        max-width: calc(min(80vw, 520px));
        width: 100%;
        margin: 10vh auto 0;

        display: flex;
        flex-flow: column nowrap;

        justify-content: center;
        align-items: center;
        z-index: 2;
        position: relative;

        padding: 1em;
        background: rgba($dark, 0.9);
        border-radius: 0.5em;
    }

    @keyframes gradient {
        0% {
            background-position: 11% 0%;
        }
        50% {
            background-position: 90% 100%;
        }
        100% {
            background-position: 11% 0%;
        }
    }

    .title {
        font-size: 4em;
        font-weight: lighter;
        font-family: "adlery-pro", cursive;
        width: max-content;

        display: block;
        text-align: center;
        transform: rotate(-5deg);

        color: transparent;
        background-image: linear-gradient(117deg, $primary, $tertiary);
        background-size: 400% 400%;
        background-clip: text;

        animation: gradient 5s ease infinite;
    }

    .widget {
        width: 100%;

        input,
        select {
            display: block;
            width: 100%;
            margin-top: 0.5em;
            padding: 0.5em;

            border: none;
            // outline: none;
            background: darken($dark, 5);
            color: $light;
            border-radius: 4px;
        }

        button {
            margin-top: 1em;
            float: right;

            border: none;
            border-radius: 4px;
            padding: 0.5em 1em;
            color: $light;
            font-weight: bold;

            background: linear-gradient(90deg, $primary, $tertiary);

            transform: translate(-1px, -2px);
            box-shadow: 1px 2px 1px black;

            &:hover,
            &:focus-within {
                background: linear-gradient(
                    90deg,
                    color.scale($primary, $lightness: 10%),
                    color.scale($tertiary, $lightness: 10%)
                );

                transform: translate(-2px, -4px);
                box-shadow: 2px 4px 2px black;
            }

            &:active {
                background: linear-gradient(
                    90deg,
                    color.scale($primary, $lightness: -10%),
                    color.scale($tertiary, $lightness: -10%)
                );

                transform: none;
                box-shadow: none;
            }

            &:disabled {
                background: linear-gradient(
                    90deg,
                    color.scale($primary, $saturation: -50%),
                    color.scale($tertiary, $saturation: -50%)
                );

                transform: none;
                box-shadow: none;
            }
        }
    }
</style>
