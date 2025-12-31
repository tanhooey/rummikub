import type { Dispatch, SetStateAction } from 'react'
import { useNavigate } from 'react-router'


type PRELOBBY_STATES = "default" | "join_game" | "create_game"

export default function WindowButtonComponent({
    name,
    targetState,
    set_prelobby_state,
}: {
    name: string
    targetState?: PRELOBBY_STATES
    set_prelobby_state?: Dispatch<SetStateAction<PRELOBBY_STATES>>
}) {
    let navigate = useNavigate();
    const handleClick = () => {
        if (targetState && targetState === "create_game") {
            console.log('here')
            navigate("/test")
        }
        else if (set_prelobby_state && targetState) 
            set_prelobby_state(targetState)
    }

    return <>
        <button onClick={handleClick} className="bg-blue-500 m-2 hover:bg-blue-400 text-white font-bold py-2 px-4 border-b-4 border-blue-700 hover:border-blue-500 rounded">
            {name}
        </button>
    </>
}