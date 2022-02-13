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

    const onMouseDown = (e) => {
        mouseDowning.current = true
        lastPos.current = [e.clientX, e.clientY]
    }

    const onMouseMove = (e) => { 
        if (mouseDowning.current) {
            const offsetX = e.clientX - lastPos.current[0]
            const offsetY = e.clientY - lastPos.current[1]
            
            lastPos.current = [e.clientX, e.clientY]
        
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
        return () => {
            document.onmousemove = null
            document.onmouseup = null
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
        />
        {
            props.children
        }
    </Paper>
}