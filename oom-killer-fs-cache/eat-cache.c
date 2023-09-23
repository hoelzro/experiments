#include <assert.h>
#include <ctype.h>
#include <errno.h>
#include <fcntl.h>
#include <getopt.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

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

static int
parse_bytes(const char *s, unsigned long long *out)
{
    char *end;
    long mult = -1;
    int i;

    *out = strtoull(s, &end, 10);
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
#define HANDLE(flag_value)\
    if(!strcmp(s, #flag_value)) {\
        *out = flag_value;\
        return 0;\
    }

    HANDLE(MADV_NORMAL);
    HANDLE(MADV_RANDOM);
    HANDLE(MADV_SEQUENTIAL);
    HANDLE(MADV_WILLNEED);
    HANDLE(MADV_DONTNEED);

#undef HANDLE

    return -1;
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

static int
has_prefix(const char *s, const char *prefix)
{
    return !strncmp(s, prefix, strlen(prefix));
}

static void
convert_kb(char *line)
{
    char *p;
    long kb;
    size_t remaining_space;
    size_t bytes_written;

    p = strstr(line, "kB");
    assert(p);

    p--;

    // back up over spaces between the amount and "kB"
    while(p >= line && isspace(*p)) {
        p--;
    }

    // back up to the beginning of the amount
    while(p >= line && isdigit(*p)) {
        p--;
    }
    assert(p >= line);

    p++;
    assert(isdigit(*p));

    kb = strtol(p, NULL, 10);

    remaining_space = strlen(line) + 1 - (p - line);
    bytes_written = snprintf(p, remaining_space, "%.2f mB\n", kb / 1024.0);

    if(bytes_written >= remaining_space) {
        // if we ran out of space, it's probably the case that it was something like
        // "0 kB" - so back enough over enough spaces before the number to provide
        // enough room to fit
        do {
            p--;
            remaining_space++;
        } while(p >= line && isspace(*p) && bytes_written >= remaining_space);
        assert(p >= line);
        assert(isspace(*p));

        // …and then try again
        bytes_written = snprintf(p, remaining_space, "%.2f mB\n", kb / 1024.0);
        assert(bytes_written < remaining_space);
    }
}

static void
convert_bytes(char *line)
{
    char *p;
    long bytes;
    size_t remaining_space;
    size_t bytes_written;

    p = line + strlen(line) - 1;

    // trim trailing newlines
    while(p >= line && *p == '\n') {
        p--;
    }
    assert(p >= line);

    // back up to the beginning of the amount
    while(p >= line && isdigit(*p)) {
        p--;
    }
    assert(p >= line);

    p++;
    assert(isdigit(*p));

    bytes = strtol(p, NULL, 10);

    remaining_space = strlen(line) + 1 - (p - line);
    bytes_written = snprintf(p, remaining_space, "%.2f mB\n", bytes / 1048576.0);

    // we're reading things from memory.stat, which doesn't include a nice amount
    // of padding before the value :(
    assert(bytes_written < remaining_space);
}

static void
print_memory_report(void)
{
    FILE *fp;
    static char *line = NULL;
    static size_t len = 0;

    char *cgroup;
    static char cgroup_memory_stat_path[PATH_MAX];

    fp = fopen("/proc/self/status", "r");
    if(!fp) {
        die("unable to open /proc/self/status for reading: %s", strerror(errno));
    }

    while((getline(&line, &len, fp)) != -1) {
        if(has_prefix(line, "Vm") || has_prefix(line, "Rss")) {
            convert_kb(line);
            printf("%s", line);
        }
    }

    if(!feof(fp)) {
        die("unable to read from /proc/self/status: %s", strerror(errno));
    }

    fclose(fp);

    printf("---\n");

    fp = fopen("/proc/meminfo", "r");
    if(!fp) {
        die("unable to open /proc/meminfo for reading: %s", strerror(errno));
    }

    while((getline(&line, &len, fp)) != -1) {
        if(strcasestr(line, "active(file)")) {
            convert_kb(line);
            printf("%s", line);
        }
    }

    if(!feof(fp)) {
        die("unable to read from /proc/meminfo: %s", strerror(errno));
    }

    fclose(fp);

    printf("---\n");

    fp = fopen("/proc/self/cgroup", "r");
    if(!fp) {
        die("unable to open /proc/self/cgroup for reading: %s", strerror(errno));
    }

    getline(&line, &len, fp);

    if(ferror(fp)) {
        die("unable to read from /proc/self/cgroup: %s", strerror(errno));
    }

    fclose(fp);

    cgroup = line;
    cgroup = strchr(cgroup, ':') + 1;
    cgroup = strchr(cgroup, ':') + 1;
    assert(!strchr(cgroup, ':'));
    if(cgroup[0] == '/') {
        cgroup++;
    }
    assert(cgroup[strlen(cgroup)-1] == '\n');
    cgroup[strlen(cgroup)-1] = '\0';

    snprintf(cgroup_memory_stat_path, sizeof(cgroup_memory_stat_path), "/sys/fs/cgroup/%s/memory.stat", cgroup);

    fp = fopen(cgroup_memory_stat_path, "r");
    if(!fp) {
        die("unable to open %s for reading: %s", cgroup_memory_stat_path, strerror(errno));
    }

    while((getline(&line, &len, fp)) != -1) {
        if(strcasestr(line, "active_file")) {
            convert_bytes(line);
            printf("%s", line);
        }
    }

    if(!feof(fp)) {
        die("unable to read from %s: %s", cgroup_memory_stat_path, strerror(errno));
    }

    fclose(fp);

    printf("---\n");

    system("free -m");

    printf("\n");

    free(line);
}

static void
populate_fs_cache_regular_io(unsigned long long bytes_to_read, unsigned long long dump_interval, int argc, char **argv)
{
    int i;
    char buf[8192];

    unsigned long long bytes_read_in       = 0;
    unsigned long long total_bytes_read_in = 0;

    for(i = 0; i < argc; i++) {
        int fd;
        ssize_t nbytes;

        fd = open(argv[i], O_RDONLY);
        if(fd == -1) {
            die("unable to open %s for reading: %s", argv[i], strerror(errno));
        }
        while((nbytes = read(fd, buf, sizeof(buf))) && nbytes > 0) {
            bytes_read_in += nbytes;
            total_bytes_read_in += nbytes;

            if(bytes_read_in > dump_interval) {
                print_memory_report();
                bytes_read_in -= dump_interval;
            }

            if(total_bytes_read_in > bytes_to_read) {
                break;
            }
        }
        if(nbytes == -1) {
            die("unable to read from %s: %s", argv[i], strerror(errno));
        }
        close(fd);

        if(total_bytes_read_in > bytes_to_read) {
            break;
        }
    }
}

int
main(int argc, char **argv)
{
    int opt;
    int status;

    unsigned long long bytes_to_read  = 0;
    unsigned long long bytes_to_alloc = 0;
    int use_mmap                      = 0;
    unsigned long long mmap_limit     = 0;
    int madvise_flag                  = MADV_NORMAL;
    unsigned long long dump_interval  = GIBIBYTE;
    int sleep_time                    = 0;

    while((opt = getopt_long(argc, argv, "", options, NULL)) != -1) {
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

    populate_fs_cache_regular_io(bytes_to_read, dump_interval, argc - optind, argv + optind);
    
    return 0;
}
