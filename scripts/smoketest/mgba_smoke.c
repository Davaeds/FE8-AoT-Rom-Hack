/*
 * mgba_smoke: run a GBA ROM headlessly in libmgba, follow a tiny input
 * script, and dump screenshots as PPM files. Used to smoke-test builds
 * in environments with no display (e.g. cloud sessions).
 *
 * Usage: mgba_smoke ROM OUTDIR SCRIPT
 *
 * SCRIPT lines (blank lines and lines starting with # are ignored):
 *   wait N              run N frames with no keys held
 *   press KEYS [N]      hold KEYS for N frames (default 4), then 1 frame released
 *                       KEYS is one or more of A B SELECT START RIGHT LEFT UP DOWN R L
 *                       joined with '+', e.g. A+B
 *   shot NAME           write OUTDIR/NAME.ppm (240x160 RGB)
 *   dump NAME ADDR LEN  write LEN bytes of the bus from ADDR (hex) to OUTDIR/NAME.bin
 *   record NAME         start writing the sound output to OUTDIR/NAME.wav
 *                       (stereo, 16-bit, 32768 Hz) until "stop"
 *   stop                finish the recording
 *   songlog             from now on, print "song FRAME PLAYER ID" whenever one of
 *                       the first four music players starts a new song (ID is
 *                       the song table index, or -1 if not found)
 *
 * For each shot, prints "shot NAME frame=F fnv1a=HASH" to stdout so two runs
 * can be compared without looking at the images.
 */
#include <mgba/core/blip_buf.h>
#include <mgba/core/core.h>
#include <mgba/core/log.h>
#include <mgba/internal/gba/input.h>

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void quietLog(struct mLogger* logger, int category, enum mLogLevel level, const char* format, va_list args) {
	(void) logger;
	(void) category;
	(void) level;
	(void) format;
	(void) args;
}

static unsigned width, height;
static color_t* video;
static unsigned long frame;
static FILE* wav;
static unsigned long wavSamples;

#define AUDIO_RATE 32768

static void put32(FILE* f, uint32_t v) {
	for (int i = 0; i < 4; ++i) {
		fputc((v >> (8 * i)) & 0xFF, f);
	}
}

static void wavHeader(FILE* f, uint32_t samples) {
	fseek(f, 0, SEEK_SET);
	fwrite("RIFF", 1, 4, f);
	put32(f, 36 + samples * 4);
	fwrite("WAVEfmt ", 1, 8, f);
	put32(f, 16);
	put32(f, 1 | (2 << 16));              /* PCM, 2 channels */
	put32(f, AUDIO_RATE);
	put32(f, AUDIO_RATE * 4);
	put32(f, 4 | (16 << 16));             /* block align 4, 16 bits */
	fwrite("data", 1, 4, f);
	put32(f, samples * 4);
}

/* Drain the emulator's sound buffers every frame; keep the samples while recording. */
static void audio(struct mCore* core) {
	struct blip_t* l = core->getAudioChannel(core, 0);
	struct blip_t* r = core->getAudioChannel(core, 1);
	short buf[2048];
	int avail;
	while ((avail = blip_samples_avail(l)) > 0) {
		if (avail > 1024) {
			avail = 1024;
		}
		blip_read_samples(l, buf, avail, 1);
		blip_read_samples(r, buf + 1, avail, 1);
		if (wav) {
			for (int i = 0; i < avail * 2; ++i) {
				fputc(buf[i] & 0xFF, wav);
				fputc((buf[i] >> 8) & 0xFF, wav);
			}
			wavSamples += (unsigned long) avail;
		}
	}
}

/* FE8U sound tables: music players (12 bytes each, MusicPlayerInfo pointer
 * first) and songs (8 bytes each, song header pointer first). */
#define MPLAYER_TABLE 0x08224404u
#define SONG_TABLE 0x08224470u
static int songlog;
static uint32_t lastHeader[4];

static void logSongs(struct mCore* core) {
	for (int p = 0; p < 4; ++p) {
		uint32_t info = core->busRead32(core, MPLAYER_TABLE + 12 * p);
		uint32_t header = core->busRead32(core, info);
		if (header == lastHeader[p]) {
			continue;
		}
		lastHeader[p] = header;
		int id = -1;
		for (int i = 0; i < 0x400 && id < 0; ++i) {
			if (core->busRead32(core, SONG_TABLE + 8 * i) == header) {
				id = i;
			}
		}
		printf("song %lu %d 0x%X\n", frame, p, (unsigned) id);
	}
}

static void step(struct mCore* core, uint32_t keys, unsigned frames) {
	core->setKeys(core, keys);
	for (unsigned i = 0; i < frames; ++i) {
		core->runFrame(core);
		audio(core);
		++frame;
		if (songlog) {
			logSongs(core);
		}
	}
}

static int parseKeys(char* spec, uint32_t* keys) {
	static const char* names[] = { "A", "B", "SELECT", "START", "RIGHT", "LEFT", "UP", "DOWN", "R", "L" };
	*keys = 0;
	for (char* tok = strtok(spec, "+"); tok; tok = strtok(NULL, "+")) {
		int found = 0;
		for (int k = 0; k < GBA_KEY_MAX; ++k) {
			if (strcmp(tok, names[k]) == 0) {
				*keys |= 1u << k;
				found = 1;
			}
		}
		if (!found) {
			fprintf(stderr, "unknown key: %s\n", tok);
			return 0;
		}
	}
	return 1;
}

static int shot(const char* outdir, const char* name) {
	char path[4096];
	snprintf(path, sizeof(path), "%s/%s.ppm", outdir, name);
	FILE* f = fopen(path, "wb");
	if (!f) {
		perror(path);
		return 0;
	}
	fprintf(f, "P6\n%u %u\n255\n", width, height);
	uint32_t hash = 2166136261u;
	for (unsigned i = 0; i < width * height; ++i) {
		/* 32-bit mGBA builds store pixels as 0xXXBBGGRR */
		uint32_t px = (uint32_t) video[i];
		unsigned char rgb[3] = { px & 0xFF, (px >> 8) & 0xFF, (px >> 16) & 0xFF };
		fwrite(rgb, 1, 3, f);
		for (int c = 0; c < 3; ++c) {
			hash = (hash ^ rgb[c]) * 16777619u;
		}
	}
	fclose(f);
	printf("shot %s frame=%lu fnv1a=%08x\n", name, frame, hash);
	return 1;
}

int main(int argc, char** argv) {
	if (argc != 4) {
		fprintf(stderr, "usage: %s ROM OUTDIR SCRIPT\n", argv[0]);
		return 2;
	}
	struct mLogger logger = { .log = quietLog, .filter = NULL };
	mLogSetDefaultLogger(&logger);

	struct mCore* core = mCoreFind(argv[1]);
	if (!core || !core->init(core)) {
		fprintf(stderr, "could not create a core for %s\n", argv[1]);
		return 1;
	}
	mCoreInitConfig(core, NULL);
	core->desiredVideoDimensions(core, &width, &height);
	video = calloc((size_t) width * height, sizeof(color_t));
	core->setVideoBuffer(core, video, width);
	if (!mCoreLoadFile(core, argv[1])) {
		fprintf(stderr, "could not load %s\n", argv[1]);
		return 1;
	}
	core->reset(core);
	core->setAudioBufferSize(core, 4096);
	blip_set_rates(core->getAudioChannel(core, 0), core->frequency(core), AUDIO_RATE);
	blip_set_rates(core->getAudioChannel(core, 1), core->frequency(core), AUDIO_RATE);

	FILE* script = fopen(argv[3], "r");
	if (!script) {
		perror(argv[3]);
		return 1;
	}
	char line[512];
	int lineno = 0, ok = 1;
	while (ok && fgets(line, sizeof(line), script)) {
		++lineno;
		char cmd[32] = "", arg[256] = "";
		unsigned n = 0;
		int fields = sscanf(line, "%31s %255s %u", cmd, arg, &n);
		if (fields <= 0 || cmd[0] == '#') {
			continue;
		}
		if (strcmp(cmd, "wait") == 0 && fields >= 2) {
			step(core, 0, (unsigned) strtoul(arg, NULL, 10));
		} else if (strcmp(cmd, "press") == 0 && fields >= 2) {
			uint32_t keys;
			ok = parseKeys(arg, &keys);
			if (ok) {
				step(core, keys, fields >= 3 ? n : 4);
				step(core, 0, 1);
			}
		} else if (strcmp(cmd, "dump") == 0) {
			char name[64];
			unsigned addr, len;
			if (sscanf(line, "%*s %63s %x %x", name, &addr, &len) != 3) {
				fprintf(stderr, "%s:%d: dump NAME ADDR LEN\n", argv[3], lineno);
				ok = 0;
			} else {
				char path[4096];
				snprintf(path, sizeof(path), "%s/%s.bin", argv[2], name);
				FILE* f = fopen(path, "wb");
				for (unsigned i = 0; f && i < len; ++i) {
					fputc(core->busRead8(core, addr + i), f);
				}
				if (f) {
					fclose(f);
				}
			}
		} else if (strcmp(cmd, "record") == 0 && fields >= 2) {
			char path[4096];
			snprintf(path, sizeof(path), "%s/%s.wav", argv[2], arg);
			if (wav) {
				wavHeader(wav, (uint32_t) wavSamples);
				fclose(wav);
			}
			wav = fopen(path, "wb");
			wavSamples = 0;
			if (wav) {
				wavHeader(wav, 0);
			} else {
				perror(path);
				ok = 0;
			}
		} else if (strcmp(cmd, "stop") == 0) {
			if (wav) {
				wavHeader(wav, (uint32_t) wavSamples);
				fclose(wav);
				wav = NULL;
			}
		} else if (strcmp(cmd, "songlog") == 0) {
			songlog = 1;
		} else if (strcmp(cmd, "shot") == 0 && fields >= 2) {
			ok = shot(argv[2], arg);
		} else {
			fprintf(stderr, "%s:%d: cannot parse: %s", argv[3], lineno, line);
			ok = 0;
		}
	}
	fclose(script);
	if (wav) {
		wavHeader(wav, (uint32_t) wavSamples);
		fclose(wav);
	}
	core->deinit(core);
	free(video);
	return ok ? 0 : 1;
}
