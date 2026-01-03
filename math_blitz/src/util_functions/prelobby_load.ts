const setSessionCookie = async () => {
    const response = await fetch("http://0.0.0.0:8000/api/start_session", {
        credentials: 'include'  // Required to send/receive cookies
    })
    if (!response.ok) {
        throw new Error('Failed to fetch items');
    }
}
export default setSessionCookie