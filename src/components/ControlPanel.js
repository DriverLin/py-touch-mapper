import { useEffect, useRef, useState } from "react";

export default function ControlPanel(props) {
    const KeySetting = (props) => {
        const [KeySetting, setKeySetting] = useState(() => props.data);
        
        const pushChange = (value) => { 
            props.setSingleKeyMap(props.data.key, value)
            setKeySetting({...KeySetting,...value})
        }
        
        return <div style={{
            width: "100%",
            height: "60px",
            border: "1px solid #d90051",
            display: "flex",
            flexDirection: "column",
        }}
            // onClick={() => { 
            //     pushChange({"action": "click"})
            // }}
        >
            <a>{`${KeySetting.key} : (${KeySetting.x},${KeySetting.y})`}</a>
            <a>{`动作 : ${KeySetting.type}` }</a>


        </div>
    }

    const setSingleKeyMap = (key, values) => {
        const copy = props.keyMap
        let index = -1 
        for (let i = 0; i < copy.length; i++) {
            if (copy[i].key === key) {
                index = i
                break
            }
        }
        if (index === -1) return
        copy[index] = { ...copy[index], ...values }
        props.setKeyMap(copy)
        console.log(copy)
    }


    return <div
        style={{
            width: "300px",
            height: "600px",
            overflow: "scroll",
            backgroundColor: "#ffffff",
            display: "flex",
            flexDirection: "column",
        }}
    >
        {props.keyMap.map((keyData, index) => <KeySetting key={index} data={keyData} setSingleKeyMap={setSingleKeyMap} />)}

    </div>
}