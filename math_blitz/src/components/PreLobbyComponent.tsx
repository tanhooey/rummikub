import { useState } from 'react'
import type {FormEvent} from 'react'
type PRELOBBY_STATES = "default" | "find_game" | "join_game" | "create_game"
import Button from './Button'
import { useNavigate } from 'react-router'
import TextInput from './TextInput'

export default function PreLobbyComponent() {
    const [prelobby_state, set_prelobby_state] = useState<PRELOBBY_STATES>("default")
    const navigate = useNavigate()
    switch (prelobby_state) {
        case "default":
            return <>
                <Button name={"Join Game"}
                    onClick={() => set_prelobby_state("find_game")} />
                <Button name={"Create Game"}
                    onClick={() => set_prelobby_state("create_game")} />
            </>
        case "find_game":
            const handleJoinGame = async (e: FormEvent<HTMLFormElement>) => {
                e.preventDefault();
                const formData = new FormData(e.currentTarget);
                const lobbyCode = formData.get("Lobby_Code") as string;
                const playerName = formData.get("Name") as string;

                // Make API call
                const response = await fetch(`http://0.0.0.0:8000/api/join_game`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({
                        player_name: playerName, // Get from somewhere
                        game_id: lobbyCode
                    })
                });

                if (response.ok) {
                    console.log(response)
                }
            };
            return <>
                <form onSubmit={handleJoinGame}>
                    <TextInput fieldLabel={"Name"} />
                    <TextInput fieldLabel={"Lobby Code"} />
                    <Button
                        name={"Back"}
                        onClick={() => {
                            navigate("/")
                            set_prelobby_state("default")
                        }
                        } />
                    <Button
                        name={"Join"}
                        type={"submit"}
                    // onClick={() => set_prelobby_state("create_game")}
                    />
                </form>
            </>
        case "create_game":
            return <></>
        default:
            return <></>
    }
}