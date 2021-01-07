import React, { Component } from 'react';
import RoomJoinPage from "./RoomJoinPage";
import CreateRoomPage from "./CreateRoomPage";
import Room from "./Room";
import { BrowserRouter as Router, Switch, Route, Link, Redirect } from "react-router-dom";

export default class HomePage extends Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <Router>
                <switch>
                    <Route exact path='/'><p>This is the home page</p>   </Route>
                    <Route path='/join' component={RoomJoinPage} />
                    <Route path='/create' component={CreateRoomPage} />
                    {/* react router by default passes props to the room component that will have info relating to how we got there. It'll give a prop called match (how it matched the url string path) and that will give access to the params from the url. Grab room code from there. */}
                    <Route path='/room/:roomCode' component={Room} />
                </switch>
            </Router>);

    }
}