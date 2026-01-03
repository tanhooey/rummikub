import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import PreLobby from './PreLobby.tsx'
import { createBrowserRouter, RouterProvider, BrowserRouter, Routes, Route } from "react-router";
import setSessionCookie from './util_functions/prelobby_load.ts';

const router = createBrowserRouter([
  {
    path: "/",
    element: <PreLobby/>,
    loader: setSessionCookie
  }
])
createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <RouterProvider router={router}/>
  </StrictMode>
)
