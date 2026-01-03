export default function Button({
    name,
    type = "button",
    onClick
}: {
    name: string
    type?: "button" | "submit" | "reset"
    onClick?: () => {} | void
}) {

    return <>
        <button type={type} onClick={onClick} className="bg-blue-500 m-2 hover:bg-blue-400 text-white font-bold py-2 px-4 border-b-4 border-blue-700 hover:border-blue-500 rounded">
            {name}
        </button>
    </>
}