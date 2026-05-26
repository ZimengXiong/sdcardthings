cmake_minimum_required(VERSION 3.20)
project(led_config_test C)

set(CMAKE_C_STANDARD 11)
set(CMAKE_C_STANDARD_REQUIRED ON)

add_executable(led_config_test
    led_config.c
    test_led_config.c
)

target_compile_options(led_config_test PRIVATE -Wall -Wextra -Wpedantic)

