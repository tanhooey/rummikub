export default function NameComponent({ fieldLabel }: { fieldLabel: string }) {
    return (
        <>
            <div>
                <label className="m-2" htmlFor="name">
                    {fieldLabel}
                </label>
                <input
                    className="p-1 border border-black"
                    type="text"
                    id="name"
                    required
                    minLength={3}
                    size={16}
                />
            </div>
        </>
    )
}