# audio test
from io import BytesIO
from struct import unpack_from
from machine import I2S, Pin

SCK_PIN = 18
WS_PIN = 19
SD_PIN = 20
I2S_ID = 0
BUFFER_LENGTH_IN_BYTES = 5000


def play_wav_file(file, ):
    wav: BytesIO = open(file, "rb")

    # read sampling rates et. al. from wav file header
    header = wav.read(44)
    (fmt, channels, sampling_rate, bit_rate, block_size,
     bits_per_sample) = unpack_from("hhiihh", header, 20)

    if fmt != 1:
        raise Exception(
            "we only support PCM formatted WAV files."
        )

    if channels > 2:
        raise Exception(
            "we don't support more than two channels. We only have one speaker anyway...")

    print("%s :: %i bit PCM, %iHz sampling rate" %
          (file, bits_per_sample, sampling_rate))

    audio_out = I2S(
        I2S_ID,
        sck=Pin(SCK_PIN),
        ws=Pin(WS_PIN),
        sd=Pin(SD_PIN),
        mode=I2S.TX,
        bits=bits_per_sample,
        format=I2S.MONO if channels == 1 else I2S.STEREO,
        rate=sampling_rate,
        ibuf=BUFFER_LENGTH_IN_BYTES,
    )

    _ = wav.seek(44)  # advance to first byte of Data section in WAV file

    # allocate sample array
    # memoryview used to reduce heap allocation
    wav_samples = bytearray(1000)
    wav_samples_mv = memoryview(wav_samples)

    # continuously read audio samples from the WAV file
    # and write them to an I2S DAC
    print("==========  START PLAYBACK ==========")

    try:
        while True:
            num_read = wav.readinto(wav_samples_mv)
            # end of WAV file?
            if num_read == 0:
                # end-of-file, advance to first byte of Data section
                print("======== DONE =========")
                break

            _ = audio_out.write(wav_samples_mv[:num_read])

    except (KeyboardInterrupt, Exception) as e:
        print("caught exception {} {}".format(type(e).__name__, e))

    # cleanup
    wav.close()
    audio_out.deinit()
