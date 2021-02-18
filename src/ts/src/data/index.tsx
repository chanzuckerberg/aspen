import React, { FunctionComponent } from "react";
import { Switch, Route, Link } from "react-router-dom";
import { Menu, Search, Container } from "semantic-ui-react";

import Samples from "./samples";

import style from "./index.module.scss";

const dummySamples: Array<Sample> = [
    {
        id: 1,
        privateId: "0865-0004KGK00-001",
        publicId: "0909EEEE-55-33",
        uploadDate: "2/1/2021",
        collectionDate: "12/12/2020",
        collectionLocation: "Santa Clara County",
        gisaid: "Accepted",
    },
    {
        id: 2,
        privateId: "0865-0004KGK00-001",
        publicId: "0909EEEE-55-33",
        uploadDate: "2/1/2021",
        collectionDate: "12/12/2020",
        collectionLocation: "Santa Clara County",
        gisaid: "Accepted",
    }
]

type Props = {
    samples?: Array<Sample>;
    trees?: Array<Tree>;
};

const Data: FunctionComponent<Props> = ({ samples = dummySamples, trees = [] }) => {
    return (
        <div className={style.dataRoot}>
            <div className={style.navigation}>
                <Menu className={style.menu} pointing secondary>
                    <Container className={style.container} fluid>
                        <Menu.Item className={style.menuItem}>
                            <div className={style.searchBar}>
                                <Search />
                            </div>
                        </Menu.Item>
                        <Link to="/data/samples">
                        <Menu.Item className={style.menuItem}>
                            <div className={style.category}>
                                <span className={style.title}>Samples</span>
                                <span className={style.count}>{samples.length}</span>
                            </div>
                        </Menu.Item>
                        </Link>
                        <Link to="/data/trees">
                        <Menu.Item className={style.menuItem}>
                            <div className={style.category}>
                                <span className={style.title}>Phylogenetic Trees</span>
                                <span className={style.count}>{trees.length}</span>
                            </div>
                        </Menu.Item>
                        </Link>
                    </Container>
                </Menu>
            </div>
            <div className={style.view}>
                <Switch>
                    <Route path="/data/samples" render={() => <Samples samples={samples}/>}/>
                    <Route path="/data/trees" render={() => <div>Phylogenetic Trees</div>}/>
                </Switch>
            </div>
        </div>
    )
}

export default Data;
