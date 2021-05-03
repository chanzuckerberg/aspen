import * as React from "react";
import { Redirect, Route, RouteProps, useLocation } from "react-router";
import { ROUTES } from "src/common/routes";

interface Props extends RouteProps {
  isLoggedIn: boolean;
  hasAgreedTerms: boolean;
}

const ProtectedRoute = (props: Props): JSX.Element => {
  const location = useLocation();

  const { component, isLoggedIn, hasAgreedTerms } = props;

  if (!isLoggedIn) {
    return <Redirect to={ROUTES.HOMEPAGE} />;
  }

  if (!hasAgreedTerms && location.pathname !== ROUTES.AGREE_TERMS) {
    return <Redirect to={ROUTES.AGREE_TERMS} />;
  }

  return <Route {...props} component={component} />;
};

export default ProtectedRoute;
