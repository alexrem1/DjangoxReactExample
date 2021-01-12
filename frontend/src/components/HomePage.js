import React, { Component } from 'react';
import RoomJoinPage from "./RoomJoinPage";
import CreateRoomPage from "./CreateRoomPage";
import Room from "./Room";
import { Grid, Button, ButtonGroup, Typography } from '@material-ui/core'
import { BrowserRouter as Router, Switch, Route, Link, Redirect } from "react-router-dom";

export default class HomePage extends Component {
    constructor(props) {
        super(props);
        this.state = {
            roomCode: null,
        };
        this.clearRoomCode = this.clearRoomCode.bind(this);
    }

    // if user is already in a Room, as the homepage/app loads, I want to direct them to back to their room if they're in a room via an endpoint I can call on the server that tells me if this user is in a room or not
    // Lifecycle mthod are ways to hook into a react component eg do something before it loads via shouldComponentUpdata
    // calling an endpoint on a server can some time eg not on the same device, client far away hence asynchronos
    async componentDidMount() {
        // call api endpoint to find out if we're in a room and if we are in a room, we get the room code coming in through the field called code. Return response.json (get json from our response). Data (json object) can be parsed through for the room code
        fetch("/api/user-in-room")
            .then((response) => response.json())
            .then((data) => {
                this.setState({
                    roomCode: data.code,
                });
            });
    }

    renderHomePage() {
        return (
            <Grid container spacing={3}>
                <Grid item xs={12} align="center">
                    <Typography variant="h3" compact="h3">
                        House Party
                    </Typography>
                </Grid>
                <Grid item xs={12} align="center">
                    <ButtonGroup disableElevation variant="contained" color="primary">
                        <Button color="primary" to="/join" component={Link}>
                            Join A Room
                        </Button>
                        <Button color="secondary" to="/create" component={Link}>
                            Create A Room
                        </Button>
                    </ButtonGroup>
                </Grid>
            </Grid>
        );
    }

    clearRoomCode() {
        this.setState({
            roomCode: null,
        });
    }

    render() {
        return (
            <Router>
                <Switch>
                    <Route
                        exact
                        path="/"
                        render={() => {
                            return this.state.roomCode ? (
                                <Redirect to={`/room/${this.state.roomCode}`} />
                            ) : (
                                    this.renderHomePage()
                                );
                        }}
                    />
                    <Route path='/join' component={RoomJoinPage} />
                    <Route path='/create' component={CreateRoomPage} />
                    {/* react router by default passes props to the room component that will have info relating to how we got there. It'll give a prop called match (how it matched the url string path) and that will give access to the params from the url. Grab room code from there. */}
                    <Route
                        path="/room/:roomCode"
                        render={(props) => {
                            return <Room {...props} leaveRoomCallback={this.clearRoomCode} />;
                        }}
                    />
                </Switch>
            </Router>
        );

    }
}