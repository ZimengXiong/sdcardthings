#include "led_config.h"

#include <assert.h>
#include <stdio.h>
#include <string.h>

static void test_hex_and_brightness(void) {
    led_config_t config;
    const char *text =
        "# sd-led-card\n"
        "brightness=64\n"
        "led0=#ff0000\n"
        "led1=#00ff40\n"
        "led2=off\n";

    led_config_init(&config, 6);
    assert(led_config_parse(&config, text, strlen(text)));
    assert(config.brightness == 64);
    assert(config.leds[0].r == 255);
    assert(config.leds[0].g == 0);
    assert(config.leds[0].b == 0);
    assert(config.leds[1].r == 0);
    assert(config.leds[1].g == 255);
    assert(config.leds[1].b == 64);
    assert(config.leds[2].r == 0);
    assert(config.leds[2].g == 0);
    assert(config.leds[2].b == 0);
}

static void test_csv_and_whitespace(void) {
    led_config_t config;
    const char *text =
        " brightness = 128 \r\n"
        " led3 = 1, 2, 3 \n"
        " led4 = 255,128,0 \n";

    led_config_init(&config, 6);
    assert(led_config_parse(&config, text, strlen(text)));
    assert(config.brightness == 128);
    assert(config.leds[3].r == 1);
    assert(config.leds[3].g == 2);
    assert(config.leds[3].b == 3);
    assert(config.leds[4].r == 255);
    assert(config.leds[4].g == 128);
    assert(config.leds[4].b == 0);
}

static void test_ignores_bad_lines(void) {
    led_config_t config;
    const char *text =
        "brightness=999\n"
        "led0=#bad\n"
        "led9=#ffffff\n"
        "led1=#010203\n";

    led_config_init(&config, 2);
    assert(led_config_parse(&config, text, strlen(text)));
    assert(config.brightness == 32);
    assert(config.leds[0].r == 0);
    assert(config.leds[1].r == 1);
    assert(config.leds[1].g == 2);
    assert(config.leds[1].b == 3);
}

int main(void) {
    test_hex_and_brightness();
    test_csv_and_whitespace();
    test_ignores_bad_lines();
    puts("led_config tests passed");
    return 0;
}

