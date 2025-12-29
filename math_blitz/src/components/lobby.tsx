export default function LobbyComponent() {
    return (
        <div>
            <label htmlFor="name">
                Username
            </label>
            <input
                type="text"
                id="name"
                required
                minLength={3}
                size={16}
            />
        </div>
    )
}