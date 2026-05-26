#include "led_config.h"

#include <ctype.h>
#include <stdlib.h>
#include <string.h>

static const char *skip_space(const char *p, const char *end) {
    while (p < end && isspace((unsigned char)*p)) {
        p++;
    }
    return p;
}

static const char *rtrim(const char *start, const char *end) {
    while (end > start && isspace((unsigned char)*(end - 1))) {
        end--;
    }
    return end;
}

static bool parse_u8(const char *start, const char *end, uint8_t *out) {
    char buf[4];
    size_t len = (size_t)(end - start);

    if (len == 0 || len > 3) {
        return false;
    }

    for (size_t i = 0; i < len; i++) {
        if (!isdigit((unsigned char)start[i])) {
            return false;
        }
        buf[i] = start[i];
    }
    buf[len] = '\0';

    long value = strtol(buf, NULL, 10);
    if (value < 0 || value > 255) {
        return false;
    }

    *out = (uint8_t)value;
    return true;
}

static int hex_nibble(char c) {
    if (c >= '0' && c <= '9') {
        return c - '0';
    }
    if (c >= 'a' && c <= 'f') {
        return 10 + c - 'a';
    }
    if (c >= 'A' && c <= 'F') {
        return 10 + c - 'A';
    }
    return -1;
}

static bool parse_hex_color(const char *start, const char *end, led_rgb_t *out) {
    if ((end - start) != 7 || start[0] != '#') {
        return false;
    }

    int n[6];
    for (size_t i = 0; i < 6; i++) {
        n[i] = hex_nibble(start[i + 1]);
        if (n[i] < 0) {
            return false;
        }
    }

    out->r = (uint8_t)((n[0] << 4) | n[1]);
    out->g = (uint8_t)((n[2] << 4) | n[3]);
    out->b = (uint8_t)((n[4] << 4) | n[5]);
    return true;
}

static bool parse_csv_color(const char *start, const char *end, led_rgb_t *out) {
    const char *parts[3] = {0};
    const char *part_ends[3] = {0};
    const char *p = start;

    for (size_t i = 0; i < 3; i++) {
        parts[i] = skip_space(p, end);
        while (p < end && *p != ',') {
            p++;
        }
        part_ends[i] = rtrim(parts[i], p);
        if (i < 2) {
            if (p >= end || *p != ',') {
                return false;
            }
            p++;
        }
    }

    if (skip_space(p, end) != end) {
        return false;
    }

    return parse_u8(parts[0], part_ends[0], &out->r) &&
           parse_u8(parts[1], part_ends[1], &out->g) &&
           parse_u8(parts[2], part_ends[2], &out->b);
}

static bool value_is_off(const char *start, const char *end) {
    return (end - start) == 3 &&
           tolower((unsigned char)start[0]) == 'o' &&
           tolower((unsigned char)start[1]) == 'f' &&
           tolower((unsigned char)start[2]) == 'f';
}

void led_config_init(led_config_t *config, size_t led_count) {
    if (led_count > LED_CONFIG_MAX_LEDS) {
        led_count = LED_CONFIG_MAX_LEDS;
    }

    config->brightness = 32;
    config->led_count = led_count;
    for (size_t i = 0; i < LED_CONFIG_MAX_LEDS; i++) {
        config->leds[i] = (led_rgb_t){0, 0, 0};
    }
}

bool led_config_parse(led_config_t *config, const char *text, size_t len) {
    bool changed = false;
    const char *p = text;
    const char *end = text + len;

    while (p < end) {
        const char *line_start = p;
        while (p < end && *p != '\n' && *p != '\r') {
            p++;
        }
        const char *line_end = rtrim(line_start, p);
        while (p < end && (*p == '\n' || *p == '\r')) {
            p++;
        }

        line_start = skip_space(line_start, line_end);
        if (line_start >= line_end || *line_start == '#') {
            continue;
        }

        const char *eq = line_start;
        while (eq < line_end && *eq != '=') {
            eq++;
        }
        if (eq >= line_end) {
            continue;
        }

        const char *key_start = line_start;
        const char *key_end = rtrim(key_start, eq);
        const char *value_start = skip_space(eq + 1, line_end);
        const char *value_end = rtrim(value_start, line_end);

        if ((key_end - key_start) == 10 &&
            strncmp(key_start, "brightness", 10) == 0) {
            uint8_t brightness;
            if (parse_u8(value_start, value_end, &brightness)) {
                config->brightness = brightness;
                changed = true;
            }
            continue;
        }

        if ((key_end - key_start) >= 4 &&
            key_start[0] == 'l' &&
            key_start[1] == 'e' &&
            key_start[2] == 'd') {
            uint8_t index;
            if (!parse_u8(key_start + 3, key_end, &index) ||
                index >= config->led_count) {
                continue;
            }

            led_rgb_t color = {0, 0, 0};
            bool parsed = false;
            if (value_is_off(value_start, value_end)) {
                parsed = true;
            } else if (parse_hex_color(value_start, value_end, &color)) {
                parsed = true;
            } else if (parse_csv_color(value_start, value_end, &color)) {
                parsed = true;
            }

            if (parsed) {
                config->leds[index] = color;
                changed = true;
            }
        }
    }

    return changed;
}

