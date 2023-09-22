#include <getopt.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <sys/mman.h>

// how many inactive files to keep open if mmap'ing
// include smaps in memory stat output?

#define FILE_BYTES_OPTION    'f'
#define ANON_BYTES_OPTION    'a'
#define USE_MMAP_OPTION      'm'
#define MMAP_LIMIT_OPTION    'l'
#define MADVISE_OPTION       'd'
#define DUMP_INTERVAL_OPTION 'i'
#define SLEEP_TIME_OPTION    's'

#define GIBIBYTE (1 << 30)

#define die(fmt, args...)\
    fprintf(stderr, fmt "\n", ##args);\
    exit(1);

static struct option options[] = {
    { .name = "file-bytes",    .has_arg = required_argument, .val = FILE_BYTES_OPTION },
    { .name = "alloc-bytes",   .has_arg = required_argument, .val = ANON_BYTES_OPTION },
    { .name = "mmap",          .has_arg = no_argument,       .val = USE_MMAP_OPTION },
    { .name = "mmap-limit",    .has_arg = required_argument, .val = MMAP_LIMIT_OPTION },
    { .name = "madvise",       .has_arg = required_argument, .val = MADVISE_OPTION },
    { .name = "dump-interval", .has_arg = required_argument, .val = DUMP_INTERVAL_OPTION },
    { .name = "sleep-time",    .has_arg = required_argument, .val = SLEEP_TIME_OPTION },
    { NULL },
};

#define NYI()\
    die("%s NYI", __FUNCTION__);

struct byte_unit {
    char *suffix;
    long mult;
};

struct byte_unit units[] = {
    { "K", 1 << 10 },
    { "M", 1 << 20 },
    { "G", 1 << 30 },
    { "", 1 },
};

static long
parse_bytes(const char *s, long *out)
{
    char *end;
    long mult = -1;
    int i;

    *out = strtol(s, &end, 10);
    if(end == s) {
        return -1;
    }

    for(i = 0; i < sizeof(units) / sizeof(units[0]); i++) {
        if(!strcmp(end, units[i].suffix)) {
            mult = units[i].mult;
            break;
        }
    }

    if(mult == -1) {
        return -1;
    }

    *out *= mult;
    return 0;
}

static int
parse_madvise(const char *s, int *out)
{
    NYI();
}

struct duration_unit {
    char *suffix;
    int mult;
};

struct duration_unit duration_units[] = {
    { "h", 60 * 60 },
    { "m", 60 },
    { "s", 1 },
    { "", 1 },
};

static int
parse_duration(const char *s, int *out)
{
    char *end;
    int mult = -1;
    int i;

    *out = strtol(s, &end, 10);
    if(end == s) {
        return -1;
    }

    for(i = 0; i < sizeof(duration_units) / sizeof(duration_units[0]); i++) {
        if(!strcmp(end, duration_units[i].suffix)) {
            mult = duration_units[i].mult;
            break;
        }
    }

    if(mult == -1) {
        return -1;
    }

    *out *= mult;
    return 0;
}

int
main(int argc, char **argv)
{
    int opt;
    int status;

    long bytes_to_read  = 0;
    long bytes_to_alloc = 0;
    int use_mmap        = 0;
    long mmap_limit     = 0;
    int madvise_flag    = MADV_NORMAL;
    int dump_interval   = GIBIBYTE;
    int sleep_time      = 0;

    while((opt = getopt_long(argc, argv, "", options, NULL))) {
        switch(opt) {
            case FILE_BYTES_OPTION:
                status = parse_bytes(optarg, &bytes_to_read);
                if(status != 0) {
                    die("unable to parse bytes for --file-bytes");
                }
                break;
            case ANON_BYTES_OPTION:
                status = parse_bytes(optarg, &bytes_to_alloc);
                if(status != 0) {
                    die("unable to parse bytes for --alloc-bytes");
                }
                break;
            case MMAP_LIMIT_OPTION:
                status = parse_bytes(optarg, &mmap_limit);
                if(status != 0) {
                    die("unable to parse bytes for --mmap-limit");
                }
                break;
            case MADVISE_OPTION:
                status = parse_madvise(optarg, &madvise_flag);
                if(status != 0) {
                    die("unable to parse flag for --madvise");
                }
                break;
            case DUMP_INTERVAL_OPTION:
                status = parse_duration(optarg, &dump_interval);
                if(status != 0) {
                    die("unable to parse duration for --dump-interval");
                }
                break;
            case SLEEP_TIME_OPTION:
                status = parse_duration(optarg, &sleep_time);
                if(status != 0) {
                    die("unable to parse duration for --sleep-time");
                }
                break;
            case USE_MMAP_OPTION:
                use_mmap = 1;
                break;
            default:
                die("usage: %s", argv[0]);
        }
    }

    // XXX drop caches
    
    return 0;
}
