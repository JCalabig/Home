from constants import *


alarm_actions = [
    {
        ACTION: SEND,
        TYPE: COMMAND,
        DEVICE: "camera",
        OP_CODE: "capture video"
    },
    {
        ACTION: SEND,
        TYPE: COMMAND,
        DEVICE: "buzzer1",
        OP_CODE: "on"
    }
]

home_monitor_config = [
    {
        STATE: BEGIN,
        NEXT_STATE: NORMAL,
        ACTIONS: [{
                ACTION: SEND,
                TYPE: COMMAND,
                DEVICE: "kitchenLights1",
                OP_CODE: "pauseEvents"
            }]
    },
    {
        STATE: ELEVATED,
        CONDITION: "event != \"reset\"",
        ACTIONS: [{
            ACTION: SEND,
            TYPE: COMMAND,
            DEVICE: "buzzer1",
            OP_CODE: "on"
        }]
    },
    {
        STATE: NORMAL,
        NEXT_STATE: ELEVATED,
        CONDITION: "event != \"reset\" and mode == \"away\"",
        ACTIONS: alarm_actions
    },
    {
        CONDITION: "event == \"panic\"",
        NEXT_STATE: ELEVATED,
        ACTIONS: alarm_actions
    },
    {
        CONDITION: "event == \"reset\"",
        NEXT_STATE: NORMAL,
        ACTIONS: [
            {
                ACTION: SET_MODE_HOME
            },
            {
                ACTION: SEND,
                TYPE: COMMAND,
                DEVICE: "kitchenLights1",
                OP_CODE: "pauseEvents"
            }
        ]
    },
    {
        CONDITION: "event == \"away\"",
        NEXT_STATE: NORMAL,
        ACTIONS: [
            {
                ACTION: SET_MODE_AWAY
            },
            {
                ACTION: SEND,
                TYPE: COMMAND,
                DEVICE: "kitchenLights1",
                OP_CODE: "resumeEvents"
            }
        ]
    }
]
