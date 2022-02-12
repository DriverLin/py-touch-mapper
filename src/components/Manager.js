import { useEffect, useRef, useState } from "react";
import ControlPanel from "./ControlPanel";
import DraggableContainer from "./DraggableContainer";

const UploadButton = (props) => {
    return <button
        style={{
            position: 'absolute',
            width: '200px',
            height: '80px',
            left: '50%',
            marginLeft: '-105px',
            top: '50%',
            borderRadius: '50px',
            border: "5px solid #00b894",
            transition: ".25s",
            fontSize: '24px',
            background: "#2C3A47",
            color: "white",
        }}
        onClick={props.onClick}>上传截图</button>

}

export default function Manager() {
    const [uploadButton, setUploadButton] = useState(true);
    const [imgUrl, setImgUrl] = useState(false);
    const imgSize = useRef([1, 1])
    const [keyMap, setKeyMap] = useState([])
    const downingKey = useRef(null)

    const uploadClick = () => {
        document.getElementById('fileInput').click();
    }

    const handleFileChange = (e) => {
        console.log(e);
        setUploadButton(false);
        const reads = new FileReader();
        reads.readAsDataURL(document.getElementById('fileInput').files[0]);
        reads.onload = function (e) {
            setImgUrl(this.result);
        };
    }

    const handelImgClick = (e) => {
        const x = e.clientX;
        const y = e.clientY;
        const key = downingKey.current;
        if (key !== null) {
            const copy = [...keyMap]
            for (let keyData of copy) {
                if (keyData.key === key) {
                    keyData.x = x
                    keyData.y = y
                    setKeyMap(copy)
                    return
                }
            }
            copy.push({
                key: key,
                x: x,
                y: y,
                type:"press"
            })
            setKeyMap(copy)
        }
    }

    useEffect(() => {
        document.onkeydown = (e) => {
            e.preventDefault();
            // console.log(e.key);
            downingKey.current = e.key
        }
        document.onkeyup = (e) => {
            downingKey.current = null
        }
        document.oncontextmenu = function (e) {
            e.preventDefault();
        };


    }, [])


    const KeyShow = (props) => {
        return <button
            style={{
                position: 'fixed',
                left: props.data.x,
                top: props.data.y,
                width: '28px',
                height: '28px',
                borderRadius: '28px',
                backgroundColor: "#d90051",
                color: "white",
                marginLeft: "-14px",
                marginTop: "-14px",
                border: "None",
                alignItems: "center",
            }}
        >
            {props.data.key}
        </button>
    }

    return (<div style={{
        width: '100vw',
        height: '100vh',
        backgroundColor: '#00796B',
    }}>

        <input id="fileInput" type="file" style={{ display: "none" }} accept="image/*" onChange={handleFileChange} ></input>

        {uploadButton ? <UploadButton onClick={uploadClick} /> : null}
        {imgUrl ? <img id="img" src={imgUrl} style={{ maxWidth: "100%", maxHeight: "100%", left: 0, top: 0 }} onClick={handelImgClick}  ></img> : null}
        {imgUrl ? <DraggableContainer>
            <ControlPanel keyMap={keyMap} setKeyMap={setKeyMap} />
        </DraggableContainer> : null}



        {
            keyMap.map((keyData, index) => {
                return <KeyShow key={index} data={keyData} />
            })
        }


    </div>)
}