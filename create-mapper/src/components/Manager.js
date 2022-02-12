import { useEffect, useRef, useState } from "react";
// import ControlPanel from "./ControlPanel";
import DraggableContainer from "./DraggableContainer";
import Grid from '@mui/material/Grid';
import { IconButton, Button, Input, Paper } from "@mui/material";
import Box from '@mui/material/Box';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import Select from '@mui/material/Select';
import { click } from "@testing-library/user-event/dist/click";
import HighlightOffIcon from '@mui/icons-material/HighlightOff';
import * as keyNameMap from "./keynamemap.json"


function copyToClipboard(text) {
    let transfer = document.createElement('input');
    document.body.appendChild(transfer);
    transfer.value = text;  // 这里表示想要复制的内容
    transfer.focus();
    transfer.select();
    if (document.execCommand('copy')) {
        document.execCommand('copy');
    }
    transfer.blur();
    document.body.removeChild(transfer);
}



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

const FixedIcon = (props) => {
    return <button
        style={{
            position: 'fixed',
            left: props.x,
            top: props.y,
            width: props.size || 28,
            height: props.size || 28,
            borderRadius: props.size || 28,
            backgroundColor: props.bgColor || "#d90051",
            color: props.textColor || "white",
            marginLeft: props.size / -2 || -14,
            marginTop: props.size / -2 || -14,
            border: "None",
            alignItems: "center",
        }}
    >
        {props.text}
    </button>
}
const GroupFixedIcon = (props) => {
    return <div>
        {
            props.pos_s.map((pos, index) => <FixedIcon
                key={index}
                x={pos[0]}
                y={pos[1]}
                size={18}
                bgColor={props.color[0]}
                textColor={props.color[1]}
                text={`${props.text}_${index}`}
            />)
        }
    </div>
}

const CostumedInput = (props) => {
    const [value, setValue] = useState(props.defaultValue)
    return <Input
        sx={{ width: props.width || "40px" }}
        inputProps={{ inputMode: 'numeric', pattern: '[0-9]*' }}
        value={value}
        onChange={(e) => {
            setValue(e.target.value.replace(/[^\d]/g, ""))
        }}
        onBlur={(e) => {
            props.onCommit(Number(value))
        }}
        onKeyDown={(e) => {
            if (e.key === "Enter") {
                props.onCommit(Number(value))
            }
        }}
    />
}

const WheelShow = (props) => { 
    const radius = props.data.range * 2 
    return <div>
        <div style={{
            position: 'fixed',
            left: props.data.pos[0],
            top: props.data.pos[1],
            width: 16,
            height: 16,
            borderRadius: 16,
            marginLeft: -8,
            marginTop: -8,
            backgroundColor: "#FF5722",
            pointerEvents: "none",
        }} />
        <div style={{
            position: 'fixed',
            left: props.data.pos[0],
            top: props.data.pos[1],
            width: radius ,
            height: radius ,
            borderRadius: radius ,
            marginLeft: radius  / -2 -4,
            marginTop: radius  / -2 -4,
            border: "4px solid #FF5722",
            pointerEvents: "none",
        }} />
    </div>
}






export default function Manager() {
    const [exportButtonText, setExportButtonText] = useState("导出")

    const [uploadButton, setUploadButton] = useState(true);
    const [imgUrl, setImgUrl] = useState(false);
    const [keyMap, setKeyMap] = useState([])
    const downingKey = useRef(null)
    const [settings, setSettings] = useState({
        "screen": {
            "size": [
                1440,
                3120
            ]
        },
        "mouse": {
            "switch_key": "key_grave",
            "pos": [
                720,
                1600
            ],
            "speed": [
                1,
                1
            ]
        },
        "wheel": {
            "pos": [
                96,
                256
            ],
            "range": 70,
            "wasd": [
                "key_w",
                "key_a",
                "key_s",
                "key_d"
            ]
        }
    })


    
    const exportJSON = () => {
        // console.log(JSON.stringify(settings, null, 4))
        const showWidth = document.getElementById("img").width
        const showHeight = document.getElementById("img").height
        const screenWidth = settings.screen.size[0]
        const screenHeight = settings.screen.size[1]
        const translateX = (x) => Math.round(x * screenWidth / showWidth) 
        const translateY = (y) => Math.round(screenHeight - y * screenHeight / showHeight)
        const translateKeyName = (jskey) => keyNameMap.default[jskey]
        const KEY_MAPS = {}
        for (let keyData of keyMap) {
            if (keyData.type === "press") {
                KEY_MAPS[translateKeyName(keyData.key)] = {
                    "TYPE": "PRESS",
                    "POS": [
                        translateX(keyData.x),
                        translateY(keyData.y)
                    ]
                }
            } else if (keyData.type === "click") {
                KEY_MAPS[translateKeyName(keyData.key)] = {
                    "TYPE": "CLICK",
                    "POS": [
                        translateX(keyData.x),
                        translateY(keyData.y)
                    ],
                    "INTERVAL": keyData.interval
                }
            } else if (keyData.type === "auto_fire") {
                KEY_MAPS[translateKeyName(keyData.key)] = {
                    "TYPE": "AUTO_FIRE",
                    "POS": [
                        translateX(keyData.x),
                        translateY(keyData.y)
                    ],
                    "INTERVAL": keyData.interval
                }
            } else if (keyData.type === "drag") {
                KEY_MAPS[translateKeyName(keyData.key)] = {
                    "TYPE": "DRAG",
                    "POS_s": keyData.pos_s.map(pos => [translateX(pos[0]), translateY(pos[1])]),
                    "INTERVAL": keyData.interval
                }
            } else if (keyData.type === "mult_press") {
                KEY_MAPS[translateKeyName(keyData.key)] = {
                    "TYPE": "MULT_PRESS",
                    "POS_s": keyData.pos_s.map(pos => [translateX(pos[0]), translateY(pos[1])]),
                }
            }

        }
        const exportResult = {
            "SCREEN": {
                "SIZE": [
                    settings.screen.size[0],
                    settings.screen.size[1]
                ]
            },
            "MOUSE": {
                "SWITCH_KEY": "KEY_GRAVE",
                "POS": settings.mouse.pos,
                "SPEED": [
                    settings.mouse.speed[0],
                    settings.mouse.speed[1]
                ]
            },
            "WHEEL": {
                "POS": [
                    translateX(settings.wheel.pos[0]),
                    translateY(settings.wheel.pos[1])
                ],
                "RANGE": translateX(settings.wheel.range),
                "WASD": [
                    "KEY_W",
                    "KEY_A",
                    "KEY_S",
                    "KEY_D"
                ]
            },
            "KEY_MAPS": KEY_MAPS
        }
        copyToClipboard(JSON.stringify(exportResult))
        setExportButtonText("已复制到剪贴板")
        setTimeout(() => {
            setExportButtonText("导出")
        }, 1000)

    }


    const OtherSettings = (props) => {
        useEffect(() => {
            const sc = new Image();
            sc.onload = () => {
                const copy = { ...settings }
                if (copy.screen.size[0] !== sc.width || copy.screen.size[1] !== sc.height) {
                    copy.screen.size = [sc.width, sc.height]
                    copy.mouse.pos = [sc.width / 2 + 40, sc.height / 2]
                    setSettings(copy)
                }

            }
            sc.src = props.screenshot;
        }, [])

        const wheelPosSelecting = useRef(false)
        const [setPosButtonDisabled, setSetPosButtonDisabled] = useState(false)
        const readyToSetPos = () => {
            wheelPosSelecting.current = true;
            setSetPosButtonDisabled(true)
        }
        const imgClickListener = (e) => {
            if (wheelPosSelecting.current) {
                const copy = { ...settings }
                copy.wheel.pos = [e.detail.clientX, e.detail.clientY]
                setSettings(copy)
                wheelPosSelecting.current = false
                setSetPosButtonDisabled(false)
            }
        }

        useEffect(() => {
            window.addEventListener('imgOnNoKeyClick', imgClickListener)
            return () => {
                window.removeEventListener('imgOnNoKeyClick', imgClickListener)
            }
        }, [])

        return <Paper sx={{
            width: "370px",
            marginLeft: "10px",
        }}>
            <Grid
                container
                spacing={"10px"}
                direction="column"
                justify="center"
                alignItems="center"
                sx={{
                    width: "350px",
                    marginLeft: "10px",
                    marginTop: "1px",
                }}
            >
                <Button
                    onClick={exportJSON}
                    variant="outlined"
                    sx={{
                        width: "100%",
                        marginTop: "10px",
                    }}
                >{exportButtonText }</Button>
                <Grid
                    container
                    direction="row"
                    justifyContent="flex-start"
                    alignItems="center"
                    sx={{
                        height: "50px",
                    }}
                >
                    <a>灵敏度&emsp;&emsp;横向 : </a>
                    <CostumedInput defaultValue={settings.mouse.speed[0]} onCommit={(value) => {
                        const copy = { ...settings }
                        copy.mouse.speed[0] = value
                        setSettings(copy)
                    }} width="40px" />
                    <a> &emsp;纵向 : </a>
                    <CostumedInput defaultValue={settings.mouse.speed[1]} onCommit={(value) => {
                        const copy = { ...settings }
                        copy.mouse.speed[1] = value
                        setSettings(copy)
                    }} width="40px" />
                </Grid>

                <Grid
                    container
                    direction="row"
                    justifyContent="flex-start"
                    alignItems="center"
                    sx={{
                        height: "50px",
                    }}>
                    <a>{`左摇杆 中心位置:(${settings.wheel.pos})`} </a>
                    <Button onClick={readyToSetPos} disabled={setPosButtonDisabled} sx={{ height: "30px", marginLeft: "10px" }} variant="outlined"  >重设</Button>
                    <a>&emsp;范围</a>
                    <CostumedInput defaultValue={settings.wheel.range} onCommit={(value) => {
                        const copy = { ...settings }
                        copy.wheel.range = value
                        setSettings(copy)
                    }} />

                </Grid>


            </Grid>
        </Paper>
    }




    const handleFileChange = (e) => {
        setUploadButton(false);
        const reads = new FileReader();
        reads.readAsDataURL(document.getElementById('fileInput').files[0]);
        reads.onload = function (e) {
            setImgUrl(this.result);
        };
    }

    const handelKeyMapChange = (key, obj) => {
        console.log("handelKeyMapChange", key, obj);
        let index = -1;
        const copy = [...keyMap]
        for (let i = 0; i < keyMap.length; i++) {
            if (keyMap[i].key === key) {
                index = i;
                break;
            }
        }
        if (index === -1) {
            copy.push(obj)
        } else {
            copy[index] = { ...copy[index], ...obj }
        }
        setKeyMap(copy)
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
                type: "press"
            })
            setKeyMap(copy)
        } else {
            if (window.dispatchEvent) {
                window.dispatchEvent(new CustomEvent('imgOnNoKeyClick', {
                    detail: e
                }))
            } else {
                window.fireEvent(new CustomEvent('imgOnNoKeyClick', {
                    detail: e,
                }));
            }

        }
    }

    useEffect(() => {
        document.onkeydown = (e) => {
            // e.preventDefault();
            // console.log(e.key);
            downingKey.current = e.key.toLowerCase();
        }
        document.onkeyup = (e) => {
            downingKey.current = null
        }
        document.oncontextmenu = function (e) {
            e.preventDefault();
        };


    }, [])

    


    const KeyShow = (props) => {
        return <div>
            {props.data.type === "press" || props.data.type === "auto_fire" || props.data.type === "click" ? <FixedIcon x={props.data.x} y={props.data.y} text={props.data.key} /> : null}
            {props.data.type === "mult_press" ? <GroupFixedIcon pos_s={props.data.pos_s} text={props.data.key} color={["#00796B","#ffffff"]}   /> : null}
            {props.data.type === "drag" ? <GroupFixedIcon pos_s={props.data.pos_s} text={props.data.key} color={["#3F51B5","#ffffff"]}  /> : null}
        </div>
    }


    



    const Type_click = (props) => {
        return <div>
            <a>点击时间 : </a>
            <CostumedInput defaultValue={props.data.interval[0]} onCommit={(value) => {
                handelKeyMapChange(props.data.key, { interval: [value] })
            }} />
            <a> ms</a>
        </div>
    }

    const Type_auto_fire = (props) => {
        return <div>
            <a>点击时长 : </a>
            <CostumedInput defaultValue={props.data.interval[0]} onCommit={(value) => {
                handelKeyMapChange(props.data.key, { interval: [value, props.data.interval[1]] })
            }} />
            <a> ms</a>

            <a> &emsp;间隔 : </a>
            <CostumedInput defaultValue={props.data.interval[1]} onCommit={(value) => {
                handelKeyMapChange(props.data.key, { interval: [props.data.interval[0], value] })
            }} />
            <a> ms</a>
        </div>
    }




    const Type_drag = (props) => {
        const waitingForClick = useRef(false)
        const [addButtonDisabled, setAddButtonDisabled] = useState(false)
        const readToAdd = () => { waitingForClick.current = true; setAddButtonDisabled(true) }
        const addKeyPoint = (x, y) => {
            const copy = props.data.pos_s;
            copy.push([x, y])
            handelKeyMapChange(props.data.key, { pos_s: copy })
        }
        const updateKeyPoint = (index, x, y) => {
            const copy = props.data.pos_s;
            copy[index] = [x, y]
            handelKeyMapChange(props.data.key, { pos_s: copy })
        }
        const removeKeyPoint = (index) => {
            const copy = props.data.pos_s;
            copy.splice(index, 1)
            handelKeyMapChange(props.data.key, { pos_s: copy })
        }

        const imgClickListener = (e) => {
            if (waitingForClick.current) {
                // console.log("imgClickListener", e.detail);
                addKeyPoint(e.detail.clientX, e.detail.clientY)
                waitingForClick.current = false;
                setAddButtonDisabled(false)
            }
        }
        useEffect(() => {
            window.addEventListener('imgOnNoKeyClick', imgClickListener)
            return () => {
                window.removeEventListener('imgOnNoKeyClick', imgClickListener)
            }
        }, [])
        const CostumedDoubleInput = (props) => {
            return <div>
                 <CostumedInput defaultValue={props.defaultValue[0]} onCommit={(value) => {
                    updateKeyPoint(props.index, value, props.defaultValue[1])
                }} />
                <a> &emsp;</a>
                <CostumedInput defaultValue={props.defaultValue[1]} onCommit={(value) => {
                    updateKeyPoint(props.index, props.defaultValue[0], value)
                }} />
            </div>
        }
        return <div>
            <Grid container >
                <Grid item xs={6}><a>间隔 : </a>
                    <CostumedInput defaultValue={props.data.interval[0]} onCommit={(value) => {
                        handelKeyMapChange(props.data.key, { interval: [value] })
                    }} />
                    <a> ms </a></Grid>
                <Grid item xs={6}><Button onClick={readToAdd} disabled={addButtonDisabled} variant="outlined" sx={{
                    height: "30px",
                    width: "105px",
                }}  >添加关键点</Button></Grid>
            </Grid>
            {
                props.data.pos_s.map((pos, index) => <div key={index} style={{ display: "flex" }}>
                    <a>{index}&emsp;</a>
                    <CostumedDoubleInput index={index} defaultValue={pos} />
                    <IconButton onClick={() => { removeKeyPoint(index) }}>
                        <HighlightOffIcon />
                    </IconButton>
                </div>
                )
            }
        </div>
    }


    const Type_mult_press = (props) => {
        const waitingForClick = useRef(false)
        const [addButtonDisabled, setAddButtonDisabled] = useState(false)
        const readToAdd = () => { waitingForClick.current = true; setAddButtonDisabled(true) }
        const addKeyPoint = (x, y) => {
            const copy = props.data.pos_s;
            copy.push([x, y])
            handelKeyMapChange(props.data.key, { pos_s: copy })
        }
        const updateKeyPoint = (index, x, y) => {
            const copy = props.data.pos_s;
            copy[index] = [x, y]
            handelKeyMapChange(props.data.key, { pos_s: copy })
        }
        const removeKeyPoint = (index) => {
            const copy = props.data.pos_s;
            copy.splice(index, 1)
            handelKeyMapChange(props.data.key, { pos_s: copy })
        }

        const imgClickListener = (e) => {
            if (waitingForClick.current) {
                // console.log("imgClickListener", e.detail);
                addKeyPoint(e.detail.clientX, e.detail.clientY)
                waitingForClick.current = false;
                setAddButtonDisabled(false)
            }
        }
        useEffect(() => {
            window.addEventListener('imgOnNoKeyClick', imgClickListener)
            return () => {
                window.removeEventListener('imgOnNoKeyClick', imgClickListener)
            }
        }, [])
        const CostumedDoubleInput = (props) => {
            return <div>
                <CostumedInput defaultValue={props.defaultValue[0]} onCommit={(value) => {
                    updateKeyPoint(props.index, value, props.defaultValue[1])
                }} />
                <a> &emsp;</a>
                <CostumedInput defaultValue={props.defaultValue[1]} onCommit={(value) => {
                    updateKeyPoint(props.index, props.defaultValue[0], value)
                }} />
            </div>
        }
        return <div>
            <Grid container >
                <Grid item xs={6}><Button onClick={readToAdd} disabled={addButtonDisabled} variant="outlined" sx={{
                    height: "30px",
                    width: "105px",
                }}  >添加触摸点</Button></Grid>
            </Grid>
            {
                props.data.pos_s.map((pos, index) => <div key={index} style={{ display: "flex" }}>
                    <a>{index}&emsp;</a>
                    <CostumedDoubleInput index={index} defaultValue={pos} />
                    <IconButton onClick={() => { removeKeyPoint(index) }}>
                        <HighlightOffIcon />
                    </IconButton>
                </div>
                )
            }
        </div>
    }

    const KeySettingRender = (props) => {
        const [value, setValue] = useState(props.data.type)
        const handleChange = (e) => {
            console.log(e.target.value)
            setValue(e.target.value)
            if (e.target.value === "click") {
                handelKeyMapChange(props.data.key, { type: "click", interval: [18] })
            } else if (e.target.value === "press") {
                handelKeyMapChange(props.data.key, { type: "press", })
            } else if (e.target.value === "auto_fire") {
                handelKeyMapChange(props.data.key, { type: "auto_fire", interval: [18, 36] })
            } else if (e.target.value === "drag") {
                handelKeyMapChange(props.data.key, { type: "drag", interval: [18], pos_s: [] })
            } else if (e.target.value === "mult_press") {
                handelKeyMapChange(props.data.key, { type: "mult_press", pos_s: [] })
            }
        }

        return <Grid
            container
            direction="column"
            padding="10px"
        >
            <Grid container
                direction="row"
            >
                {
                    props.data.type === "press" || props.data.type === "auto_fire" || props.data.type === "click" ?
                        <Grid item xs={6}><a>{`${props.data.key} : (${props.data.x} , ${props.data.y})`}</a></Grid> :
                        <Grid item xs={6}><a>{`${props.data.key} `}</a></Grid>


                }
                <Grid item xs={6}>
                    <FormControl>
                        <InputLabel id={`${props.data.key}-select`}></InputLabel>
                        <Select
                            labelId={`${props.data.key}-select-label`}
                            value={value}
                            onChange={handleChange}
                            sx={{ height: "30px", }}
                        >
                            <MenuItem value={"press"}>同步按下释放</MenuItem>
                            <MenuItem value={"click"}>单次点击</MenuItem>
                            <MenuItem value={"auto_fire"}>连发</MenuItem>
                            <MenuItem value={"drag"}>滑动</MenuItem>
                            <MenuItem value={"mult_press"}>多点触摸</MenuItem>
                        </Select>
                    </FormControl>
                </Grid>
            </Grid>
            {props.data.type === "click" ? <Type_click data={props.data} /> : null}
            {props.data.type === "auto_fire" ? <Type_auto_fire data={props.data} /> : null}
            {props.data.type === "drag" ? <Type_drag data={props.data} /> : null}
            {props.data.type === "mult_press" ? <Type_mult_press data={props.data} /> : null}



        </Grid>
    }


    const ControlPanel = () => {
        

        return <div
            style={{
                maxHeight: "80vh",
                overflowY: "scroll",
            }}
        >
            <Grid
                container
                direction="column"
                justifyContent="flex-start"
                alignItems="flex-start"
                spacing={"10px"}
                sx={{
                    width: "400px",
                    backgroundColor: "#F5F5F5",
                    paddingBottom: "10px",
                    spacing: "0px",
                    paddingTop: "10px",
                }}
            >
                <Grid item xs={12}>
                    <OtherSettings keyMap={keyMap} screenshot={imgUrl} />
                </Grid>           {
                    keyMap.map((data, index) =>
                        <Grid
                            item
                            xs={12}
                            key={JSON.stringify(data)}
                        >
                            <Paper
                                sx={{
                                    width: "370px",
                                    marginLeft: "10px",
                                }}
                            >
                                <KeySettingRender data={data} />
                            </Paper>

                        </Grid>)
                }
            </Grid>
        </div>
    }

    return (<div style={{
        width: '100vw',
        height: '100vh',
        backgroundColor: '#00796B',
    }}>

        <input id="fileInput" type="file" style={{ display: "none" }} accept="image/*" onChange={handleFileChange} ></input>

        {uploadButton ? <UploadButton onClick={() => { document.getElementById('fileInput').click(); }} /> : null}
        {imgUrl ? <img id="img" src={imgUrl} style={{ width: "100vw", left: 0, top: 0 }} onClick={handelImgClick}  ></img> : null}
        {imgUrl ? <DraggableContainer><ControlPanel /></DraggableContainer> : null}
        {
            keyMap.map((keyData, index) => {
                return <KeyShow key={index} data={keyData} />
            })
        }
        {
            imgUrl ? <WheelShow data={settings.wheel} />:null
        }
    </div>)
}