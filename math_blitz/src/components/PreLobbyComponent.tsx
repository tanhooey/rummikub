import { useState } from 'react'
type PRELOBBY_STATES = "default" | "join_game" | "create_game"
import WindowButtonComponent from './WindowButtonComponent'
import { NavLink } from "react-router";

export default function PreLobbyComponent() {
    const [prelobby_state, set_prelobby_state] = useState<PRELOBBY_STATES>("default")
    switch (prelobby_state) {
        case "default":
            return <>
                <WindowButtonComponent name={"Join Game"}
                    targetState={"join_game"}
                    set_prelobby_state={set_prelobby_state} />
                <WindowButtonComponent name={"Create Game"}
                    targetState={"create_game"}
                    set_prelobby_state={set_prelobby_state} />
            </>
        case "join_game":
            return <>
                <WindowButtonComponent name={"Back"}
                    targetState={"default"}
                    set_prelobby_state={set_prelobby_state} />
            </>
        case "create_game":
            return <></>
        default:
            return <></>
    }
}