#!/usr/bin/python


class WindowState(object):
    """
    State machine for the hub window states
    """
    LOCK_WINDOW  = 0
    MAIN_WINDOW  = 1
    LED_WINDOW   = 2
    STATS_WINDOW = 3
    VOICE_WINDOW = 4

class GraphState(object):
    """
    State machine for the hub graph states
    """
    LIGHTS  = 0
    RGB     = 1
    LATENCY = 2

class VoiceState(object):
    """
    State machine for Voice
    """
    RUNNING = 0
    STOP    = 1
    ERROR   = 2

