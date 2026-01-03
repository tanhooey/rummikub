export default function TextInput({ fieldLabel, onChangeFunction }: { fieldLabel: string, onChangeFunction?: (() => {})}) {
    const name = fieldLabel.replace(" ", "_")
    return (
        <>
            <div>
                <label className="m-2" htmlFor={name}>
                    {fieldLabel}
                </label>
                <input
                    className="p-1 border border-black"
                    type="text"
                    id={name}
                    name={name}
                    required
                    minLength={3}
                    size={16}
                    onChange={onChangeFunction}
                />
            </div>
        </>
    )
}