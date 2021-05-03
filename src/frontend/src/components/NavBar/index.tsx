import cx from "classnames";
import React from "react";
import { API } from "src/common/api";
import LogoImage from "src/common/images/logo.png";
import { ROUTES } from "src/common/routes";
import UserMenu from "./components/UserMenu";
import style from "./index.module.scss";
import { Logo, LogoAnchor } from "./style";

// (thuang): Please make sure this value is in sync with what we have in css
export const NAV_BAR_HEIGHT_PX = 50;

interface Props {
  org?: string;
  user?: string;
}

const NavBar = ({ org, user }: Props): JSX.Element => {
  const orgElements = (
    <React.Fragment>
      <div className={style.separator} />
      <div className={cx(style.item, style.org)}>{org}</div>
    </React.Fragment>
  );

  function hasOrg(): JSX.Element | null {
    if (org === undefined) {
      return null;
    } else {
      return orgElements;
    }
  }

  const orgSplash = hasOrg();

  const signInLink = (
    <a href={process.env.API_URL + API.LOG_IN}>
      <div className={cx(style.item, style.link)}>Sign In</div>
    </a>
  );

  function isLoggedIn(): JSX.Element {
    if (user) {
      return <UserMenu user={user} />;
    } else {
      return signInLink;
    }
  }

  const rightEdge = isLoggedIn();

  return (
    <div className={style.bar}>
      <div className={style.left}>
        <LogoAnchor to={ROUTES.HOMEPAGE}>
          <Logo alt="logo" src={String(LogoImage)} />
        </LogoAnchor>
        {orgSplash}
      </div>

      <div className={style.right}>{rightEdge}</div>
    </div>
  );
};

export default NavBar;
