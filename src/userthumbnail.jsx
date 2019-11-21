import React from "react"
import ReactDOM from "react-dom"


function Avatar(props) {
    return (
        <div><a href={props.user.homepage}>
            <img className="avatar"
             src={props.user.avatarUrl} alt={props.user.name}/>
        </a></div>
    )
}

function UserDescription(props) {
    return (
        <div>
            <h3>{props.user.name}</h3>
            <p>{props.user.description}</p>
        </div>
    )
}
class Userthumbnail extends React.Component {
    render() {
        return (
            <div className="thumbnail">
                <Avatar user={this.props.user}/>
                <UserDescription user={this.props.user}/>
            </div>
        );
    }
}

const fakeUser = {
    avatarUrl: "https://www.gravatar.com/avatar/061424e684d5c7f2869eec39b0f0e98b?d=identicon&s=60",
    name: "bojack",
    description: "very nice guy."
}
ReactDOM.render(<Userthumbnail user={fakeUser}/>, document.querySelector('#root'))