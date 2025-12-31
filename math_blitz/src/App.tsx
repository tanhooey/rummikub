import { useState } from 'react'
// import NameComponent from './components/NameComponent'
// import { createBrowserRouter } from "react-router";
// import { RouterProvider } from "react-router/dom";
import './App.css'
import PreLobbyComponent from './components/PreLobbyComponent'


function App() {
  type PRELOBBY_STATES = "default" | "join_game" | "create_game"
  const [prelobby_state, set_prelobby_state] = useState<PRELOBBY_STATES>("default")
  const [uiState, changeUIState] = useState("find_lobby")

  return (
    // This is a react fragment. React components can only return one parent element, 
    // so this is a way to do so without introducing unnecessary divs
    <>
      <h1>MathBlitz</h1>
      <div className="card">
      </div>
      <PreLobbyComponent />
    </>
    // User should be shown FindLobby Component when the state of inLobby is true.
    // Once the user has either joined a lobby or created a game, then the url should change to mathblitz.com/{gamelobby}
    // when the url is mathblitz.com/{gamelobby}, we should unmount the FindLobby Component and Mount the Game Lobby Component
  )
}

export default App
