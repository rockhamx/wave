// Editor
import React from "react"
import ReactDOM from "react-dom"
import { Editor } from "slate-react";
import { Value } from "slate";


const initialValue = Value.fromJSON({
    document: {
        nodes: [
            {
                object: 'block',
                type: 'paragraph',
                nodes: [
                    {
                        object: 'text',
                        text: 'A line of text in a paragraph.',
                    },
                ],
            },
        ],
    },
});

// Define our app...
class App extends React.Component {
    // Set the initial value when the app is first constructed.
    state = {
        value: initialValue,
    }

    // On change, update the app's React state with the new editor value.
    onChange = ({ value }) => {
        this.setState({ value })
    }

    onKeyDown = (event, editor, next) => {
        console.log(event.key)
    }

    // Render the editor.
    render() {
        return <Editor value={this.state.value} onChange={this.onChange} onKeyDown={this.onKeyDown} />
    }
}

export default App;
