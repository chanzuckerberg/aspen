import { ThemeProvider as EmotionThemeProvider } from "@emotion/react";
import { StylesProvider, ThemeProvider } from "@material-ui/core/styles";
import { defaultTheme } from "czifui";
import React, { FunctionComponent, useEffect, useState } from "react";
import { Route, Switch } from "react-router-dom";
import style from "./App.module.scss";
import { fetchUserData } from "./common/api";
import { ROUTES } from "./common/routes";
import NavBar from "./components/NavBar";
import ProtectedRoute from "./components/ProtectedRoute";
import AgreeTerms from "./views/AgreeTerms";
import Data from "./views/Data";
import Faq from "./views/Faq";
import Homepage from "./views/Homepage";
import Privacy from "./views/Privacy";
import Terms from "./views/Terms";

const App: FunctionComponent = () => {
  const [user, setUser] = useState<User | null>(null);
  const [org, setOrg] = useState("");
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const setUserData = async () => {
      try {
        const { group, user } = await fetchUserData();

        setUser(user);
        setOrg(group.name);
        setIsLoading(false);
      } catch (error) {
        setIsLoading(false);
      }
    };

    setIsLoading(true);
    setUserData();
  }, []);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  return (
    <StylesProvider injectFirst>
      <ThemeProvider theme={defaultTheme}>
        <EmotionThemeProvider theme={defaultTheme}>
          <div className={style.app}>
            <NavBar org={org} user={user?.name} />
            <Switch>
              <ProtectedRoute
                isLoggedIn={Boolean(user)}
                hasAgreedTerms={Boolean(user?.agreedToTos)}
                path={ROUTES.DATA}
                component={Data}
              />
              <ProtectedRoute
                isLoggedIn={Boolean(user)}
                hasAgreedTerms={Boolean(user?.agreedToTos)}
                path={ROUTES.AGREE_TERMS}
                component={AgreeTerms}
              />
              <Route path={ROUTES.TERMS} component={Terms} />
              <Route path={ROUTES.PRIVACY} component={Privacy} />
              <Route path={ROUTES.FAQ} component={Faq} />
              <Route path={ROUTES.TERMS} component={Terms} />
              <Route path={ROUTES.HOMEPAGE} component={Homepage} />
            </Switch>
          </div>
        </EmotionThemeProvider>
      </ThemeProvider>
    </StylesProvider>
  );
};

export default App;
