import React, { FunctionComponent, useEffect, useState } from "react";
import { BrowserRouter as Router, Route, Switch } from "react-router-dom";
import style from "./App.module.scss";
import { fetchUserData } from "./common/api";
import Data from "./data";
import Landing from "./Landing";
import NavBar from "./NavBar";

const App: FunctionComponent = () => {
  const [user, setUser] = useState<string | undefined>();
  const [org, setOrg] = useState<string | undefined>();

  useEffect(() => {
    const setUserData = async () => {
      const { group, user } = await fetchUserData();
      setUser(user.name);
      setOrg(group.name);
    };
    setUserData();
  }, []);

  return (
    <Router>
      <div className={style.app}>
        <NavBar org={org} user={user} />
        <div className={style.view}>
          <Switch>
            <Route path="/data" component={Data} />
            <Route path="/" component={Landing} />
          </Switch>
        </div>
      </div>
    </Router>
  );
};

export default App;
