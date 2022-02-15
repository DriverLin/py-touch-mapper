import { useEffect, useRef, useState } from "react";


export default function JoystickListener(props) {
    
    const indexButton = ["A", "B", "X", "Y", "LB", "RB", "LT", "RT", "SELECT", "START", "LS", "RS", "DPAD_UP", "DPAD_DOWN", "DPAD_LEFT", "DPAD_RIGHT", "HOME", "17", "18", "19", "20"]
    const connectedGamepad = useRef([])
    const gplastStates = useRef({})
    const pressedStack = useRef([])

    const gamepadconnected = (e) => {
        console.log("gamepad connected", navigator.getGamepads()[e.gamepad.index]);
        connectedGamepad.current.push(e.gamepad.index)
        gplastStates.current[e.gamepad.index] = {
            buttons: e.gamepad.buttons.map(btn => false),
            // axes: e.gamepad.axes.map(axis => axis)
        }
    }
    const gamepaddisconnected = (e) => { 
        console.log("gamepad connected", e.gamepad.index);
        connectedGamepad.current = [...connectedGamepad.current].filter(x => x !== e.gamepad.index)
    }

    const handelEvent = (gpIndex, btnIndex,downing) => { 
        console.log("handelEvent", "BTN_" + indexButton[btnIndex], downing);
        if (downing) {
            pressedStack.current.push(btnIndex)
        } else { 
            pressedStack.current = [...pressedStack.current].filter(x => x !== btnIndex)
        }
        if (pressedStack.current.length !== 0) {
            const index = pressedStack.current[pressedStack.current.length - 1]
            const name = "BTN_" + indexButton[index]
            props.setDowningBtn(name)
        } else { 
            props.setDowningBtn(null)
        }

    }

    const stateChecker = () => { 
        for (let gpIndex of connectedGamepad.current) { 
            const gp = navigator.getGamepads()[gpIndex];
            for (let i = 0; i < gp.buttons.length; i++) { 
                if (gp.buttons[i].pressed !== gplastStates.current[gpIndex].buttons[i]) {
                    gplastStates.current[gpIndex].buttons[i] = gp.buttons[i].pressed 
                    handelEvent(gpIndex, i, gp.buttons[i].pressed )
                }
            }
        }
    }
    useEffect(() => {
        window.addEventListener("gamepadconnected", gamepadconnected)
        window.addEventListener("gamepaddisconnected", gamepaddisconnected)
        const interval = setInterval(stateChecker, 4)
        return () => {
            window.removeEventListener("gamepadconnected", gamepadconnected)
            window.removeEventListener("gamepaddisconnected", gamepaddisconnected)
            clearInterval(interval)
        }
    }, [])
    return <div style={{display:"none"}}/>
}