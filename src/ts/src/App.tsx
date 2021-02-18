import React, { FunctionComponent } from "react";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
import { Container } from "semantic-ui-react";

import Upload from "upload";

import Landing from "Landing";
import NavBar from "NavBar";

import style from "App.module.scss";

type Props = {};

const App: FunctionComponent<Props> = ({ children }) => {
    return (
        <Router>
            <div className={style.app}>
                <div className={style.navBar}>
                    <NavBar user="Santa Clara County"/>
                </div>
                <div className={style.view}>
                    <Switch>
                        <Route path="/upload" render={() => <Upload />} />
                        <Route path="/" render={() => <Landing />} />
                    </Switch>
                </div>
            </div>
        </Router>
    );
}

export default App;
