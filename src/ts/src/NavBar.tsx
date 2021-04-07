import cx from "classnames";
import React, { FunctionComponent } from "react";
import style from "./NavBar.module.scss";

type Props = {
  org?: string;
  user?: string;
};

const NavBar: FunctionComponent<Props> = ({ org, user }: Props) => {
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

  const simpleUserMenu = <div className={style.item}>{user}</div>;

  const signInLink = (
    <a href={`${process.env.API_URL}/login`}>
      <div className={cx(style.item, style.link)}>Sign In</div>
    </a>
  );

  function isLoggedIn(): JSX.Element {
    if (user === undefined) {
      return signInLink;
    } else {
      return simpleUserMenu;
    }
  }

  const rightEdge = isLoggedIn();

  return (
    <div className={style.bar}>
      <div className={style.left}>
        <div className={style.logo}>ASPEN</div>
        {orgSplash}
      </div>
      <div className={style.center}></div>
      <div className={style.right}>{rightEdge}</div>
    </div>
  );
};

export default NavBar;
