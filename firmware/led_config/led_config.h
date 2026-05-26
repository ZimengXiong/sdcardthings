#ifndef LED_CONFIG_H
#define LED_CONFIG_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define LED_CONFIG_MAX_LEDS 8

typedef struct {
    uint8_t r;
    uint8_t g;
    uint8_t b;
} led_rgb_t;

typedef struct {
    uint8_t brightness;
    size_t led_count;
    led_rgb_t leds[LED_CONFIG_MAX_LEDS];
} led_config_t;

void led_config_init(led_config_t *config, size_t led_count);
bool led_config_parse(led_config_t *config, const char *text, size_t len);

#endif

