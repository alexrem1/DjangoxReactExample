import React, { Component } from 'react';
import Button from "@material-ui/core/Button";
import Grid from "@material-ui/core/Grid";
import Typography from "@material-ui/core/Typography";
import TextField from "@material-ui/core/TextField";
import FormHelperText from "@material-ui/core/FormHelperText";
import FormControl from "@material-ui/core/FormControl";
import { Link } from "react-router-dom";
import Radio from "@material-ui/core/Radio";
import RadioGroup from "@material-ui/core/RadioGroup";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import { FormLabel } from '@material-ui/core';
import { Collapse } from "@material-ui/core";
import Alert from "@material-ui/lab/Alert"

export default class CreateRoomPage extends Component {
    // set the default value for the props (piece of information being passed in). If we don't pass any of these props through, by default they will have these values
    static defaultProps = {
        votesToSkip: 2,
        guestCanPause: true,
        update: false,
        roomCode: null,
        updateCallback: () => { },
    }

    constructor(props) {
        super(props);
        /* we have this state in react and if we ever change or update this state it automatically refreshes and forces the component to update eg when you change the radio button or change the text field. Pressing create room button looks at current state which gets sent to the backend to create the room*/
        this.state = {
            guestCanPause: this.props.guestCanPause,
            votesToSkip: this.props.votesToSkip,
            errorMsg: "",
            successMsg: ""
        };

        // binding this method to the class so that inside of this method we have access to the this keyword.
        this.handleRoomButtonPressed = this.handleRoomButtonPressed.bind(this);
        this.handleVotesChange = this.handleVotesChange.bind(this);
        this.handleGuestCanPauseChange = this.handleGuestCanPauseChange.bind(this);
        this.handleUpdateButtonPressed = this.handleUpdateButtonPressed.bind(this);
    }

    handleGuestCanPauseChange(e) {
        this.setState({
            // If this value is equal to the string true then make what it true otherwise make it false
            guestCanPause: e.target.value === 'true' ? true : false,
        });
    }

    /* e is the object that called this function*/
    handleVotesChange(e) {
        /* Method used to modify state in react */
        this.setState({
            votesToSkip: e.target.value,
        });
    }

    handleRoomButtonPressed() {
        const requestOptions = {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                votes_to_skip: this.state.votesToSkip,
                guest_can_pause: this.state.guestCanPause,
            }),
        };
        // Send request to local host with request options which is going to have the payload which is my body, type post and headers of the content type. .then: once there's a response, let's take and convert that response into json and .then let's take the data and lets console log the data for now 
        fetch('/api/create-room', requestOptions).then((response) => response.json()
        ).then((data) => this.props.history.push("/room/" + data.code));
    }

    handleUpdateButtonPressed() {
        const requestOptions = {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                votes_to_skip: this.state.votesToSkip,
                guest_can_pause: this.state.guestCanPause,
                code: this.props.roomCode,
            }),
        };
        fetch('/api/update-room', requestOptions).then((response) => {
            if (response.ok) {
                this.setState({
                    successMsg: "Room updated succesfully!"
                })
            } else {
                this.setState({
                    errorMsg: "Error updating room..."
                });
            }
            // we do this after the fetch has finished
            this.props.updateCallback();
        });
    }

    renderCreateButtons() {
        return (<Grid container spacing={1}>
            <Grid item xs={12} align="center">
                <Button
                    color="primary"
                    variant="contained"
                    onClick={this.handleRoomButtonPressed}
                >
                    Create A Room
          </Button>
            </Grid>
            <Grid item xs={12} align="center">
                <Button color="secondary" variant="contained" to="/" component={Link}>
                    Back
          </Button>
            </Grid>
        </Grid>
        );
    }

    renderUpdateButtons() {
        return (
            <Grid item xs={12} align="center">
                <Button
                    color="primary"
                    variant="contained"
                    onClick={this.handleUpdateButtonPressed}
                >
                    Update Room
        </Button>
            </Grid>
        );
    }

    render() {
        // if we are in the update state, it'll be Update Room title, and if we're not it'll be Create a Room Title
        const title = this.props.update ? "Update Room" : "Create a Room"

        return <Grid container spacing={1}>
            <Grid item xs={12} align='center'>
                {/* if we have an error or success msg we will show the collapse, if we dont we're not going to show */}
                <Collapse
                    in={this.state.errorMsg != "" || this.state.successMsg != ""}
                >
                    {this.state.successMsg != "" ? (
                        <Alert
                            severity="success"
                            onClose={() => {
                                this.setState({ successMsg: "" });
                            }}
                        >
                            {this.state.successMsg}
                        </Alert>
                    ) : (
                            <Alert
                                severity="error"
                                onClose={() => {
                                    this.setState({ errorMsg: "" });
                                }}
                            >
                                {this.state.errorMsg}
                            </Alert>
                        )}
                </Collapse>
            </Grid>
            <Grid item xs={12} align='center'>
                <Typography component="h4" variant="h4">
                    {title}
                </Typography>
            </Grid>
            <Grid item xs={12} align='center'>
                <FormControl component='fieldset'>
                    <FormHelperText>
                        <div align='center'>
                            Guest Control of Playback State
                                        </div>
                    </FormHelperText>
                    <RadioGroup row defaultValue={this.props.guestCanPause.toString()} onChange={this.handleGuestCanPauseChange}>
                        <FormControlLabel value='true'
                            control={<Radio color='primary' />}
                            label='Play/Pause' labelPlacement='bottom' />
                        <FormControlLabel value='false'
                            control={<Radio color='secondary' />}
                            label='No control'
                            labelPlacement='bottom'
                        />
                    </RadioGroup>
                </FormControl>
            </Grid>
            <Grid item xs={12} align='center'>
                <FormControl>
                    <TextField required={true}
                        type='number'
                        onChange={this.handleVotesChange}
                        defaultValue={this.state.votesToSkip}
                        inputProps={{
                            min: 1,
                            style: { textAlign: 'center' },
                        }}
                    />
                    <FormHelperText>
                        <div align='center'>
                            Votes required to skip song
                                </div>
                    </FormHelperText>
                </FormControl>
            </Grid>
            {this.props.update ? this.renderUpdateButtons() : this.renderCreateButtons()}
        </Grid >
    }
}