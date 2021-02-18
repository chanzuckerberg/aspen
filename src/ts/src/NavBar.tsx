import React, { FunctionComponent } from "react";
import { Menu, Container, Dropdown, Image, Divider } from "semantic-ui-react";

import { ReactComponent as AspenLogo } from "common/styles/logos/AspenLogo.svg";

import style from "./NavBar.module.scss";

type Props = {
    user: string
}

const NavBar: FunctionComponent<Props> = ({ user, children }) => {
    return (
        <Menu className={style.menu} fixed='top' floated inverted borderless>
          <Container fluid>
            <Menu.Item as='a' header>
                <Image size='tiny' style={{ marginRight: '.5em' }}>
                    <AspenLogo />
                </Image>
            </Menu.Item>
            <div className={style.verticalLine}/>
            <Menu.Item as='a'><span className={style.user}>{user}</span></Menu.Item>
          </Container>
        </Menu>
    )
}

export default NavBar;
