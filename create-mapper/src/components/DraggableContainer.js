import { useEffect, useRef, useState } from "react";
import Paper from '@mui/material/Paper';

//可拖动的容器
//标题栏 ：内容
//标题若兰可拖动 内容外部传入

export default function DraggableContainer(props) { 
    
    const mouseDowning = useRef(false)
    const lastPos = useRef([0, 0])

    const [left_top, setLeft_top] = useState([0, 0])
    const left_top_ref = useRef([0, 0])


    const getMovexy = (e) => { 
        if (e.type === "touchmove" || e.type === "touchstart") {
            return [e.touches[0].clientX, e.touches[0].clientY]
        } else if (e.type === "mousedown" || e.type === "mousemove") {
            return [e.clientX, e.clientY]
        } else { 
            return [1,1]
        }
    }

    const onMouseDown = (e) => {
        mouseDowning.current = true
        lastPos.current = getMovexy(e)
    }

    const onMouseMove = (e) => { 
        if (mouseDowning.current) {
            e.preventDefault()
            const offsetX = getMovexy(e)[0] - lastPos.current[0]
            const offsetY = getMovexy(e)[1] - lastPos.current[1]
            lastPos.current = getMovexy(e)
            const new_left_top = [left_top_ref.current[0] + offsetX, left_top_ref.current[1] + offsetY]
            setLeft_top(new_left_top)
            left_top_ref.current = new_left_top

        }
    }
    const onMouseUp = (e) => { 
        mouseDowning.current = false
    }

    useEffect(() => {
        document.onmousemove = onMouseMove
        document.onmouseup = onMouseUp
        
        document.ontouchmove = onMouseMove
        document.ontouchend = onMouseUp
        return () => {
            document.onmousemove = null
            document.onmouseup = null

            document.ontouchmove = null
            document.ontouchend = null
        }
    }, [])

    
    return <Paper
        sx={{
            zIndex: 1,
            position: 'fixed',
            left: left_top[0],
            top: left_top[1],
            overflow: "hidden",
            borderRadius: "8px",
        }}
    >
        <div style={{ height: "30px", backgroundColor: "#607D8B" }}
            onMouseDown={onMouseDown}
            onTouchStart={onMouseDown}
        />
        {
            props.children
        }
    </Paper>
}