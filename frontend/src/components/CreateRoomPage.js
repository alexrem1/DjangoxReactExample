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

export default class CreateRoomPage extends Component {
    defaultVotes = 2;

    constructor(props) {
        super(props);
        /* we have this state in react and if we ever change or update this state it automatically refreshes and forces the component to update eg when you change the radio button or change the text field. Pressing create room button looks at current state which gets sent to the backend to create the room*/
        this.state = {
            guestCanPause: true,
            votesToSkip: this.defaultVotes,
        };

        // binding this method to the class so that inside of this method we have access to the this keyword.
        this.handleRoomButtonPressed = this.handleRoomButtonPressed.bind(this);

        this.handleVotesChange = this.handleVotesChange.bind(this);

        this.handleGuestCanPauseChange = this.handleGuestCanPauseChange.bind(this);
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

    render() {
        return <Grid container spacing={1}>
            <Grid item xs={12} align='center'>
                <Typography component="h4" variant="h4">
                    Create a Room
                        </Typography>
            </Grid>
            <Grid item xs={12} align='center'>
                <FormControl component='fieldset'>
                    <FormHelperText>
                        <div align='center'>
                            Guest Control of Playback State
                                </div>
                    </FormHelperText>
                    <RadioGroup row defaultValue='true' onChange={this.handleGuestCanPauseChange}>
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
                        defaultValue={this.defaultVotes}
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
            <Grid item xs={12} align='center'>
                <Button color='primary'
                    onClick={this.handleRoomButtonPressed}
                    variant='contained'>
                    Create A Room
                </Button>
            </Grid>
            <Grid item xs={12} align='center'>
                <Button color='secondary' variant='contained' to='/' component={Link}>
                    Back
                </Button>
            </Grid>
        </Grid >
    }
}