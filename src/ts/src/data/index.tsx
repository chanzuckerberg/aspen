import cx from "classnames";
import React, { FunctionComponent, useEffect, useState } from "react";
import {
  Link,
  Redirect,
  Route,
  RouteComponentProps,
  Switch,
} from "react-router-dom";
import { MenuItem, Tab } from "semantic-ui-react";
import { fetchSamples, fetchTrees } from "src/common/api";
import { DataSubview } from "src/common/components";
import { SAMPLE_HEADERS, TREE_HEADERS } from "./headers";
import style from "./index.module.scss";
import { TREE_TRANSFORMS } from "./transforms";

const TAB_MENU_OPTIONS = { secondary: true, pointing: true };

const Data: FunctionComponent<RouteComponentProps> = (props) => {
  const { location } = props;

  const [samples, setSamples] = useState<Sample[] | undefined>();
  const [trees, setTrees] = useState<Tree[] | undefined>();

  useEffect(() => {
    const setBioinformaticsData = async () => {
      const [sampleResponse, treeResponse] = await Promise.all([
        fetchSamples(),
        fetchTrees(),
      ]);
      const apiSamples = sampleResponse["samples"];
      const apiTrees = treeResponse["phylo_trees"];

      // DEBUG
      // DEBUG
      // DEBUG
      // DEBUG
      // DEBUG
      // DEBUG
      // Remove slice on PR
      setSamples(apiSamples.slice(0, 10));
      setTrees(apiTrees);
    };
    setBioinformaticsData();
  }, []);

  // this constant is inside the component so we can associate
  // each category with its respective variable.
  const dataCategories = [
    {
      data: samples,
      headers: SAMPLE_HEADERS,
      text: "Samples",
      to: "/data/samples",
    },
    {
      data: trees,
      headers: TREE_HEADERS,
      text: "Phylogenetic Trees",
      to: "/data/phylogenetic_trees",
      transforms: TREE_TRANSFORMS,
    },
  ];

  // run data through transforms
  dataCategories.forEach((category) => {
    if (category.transforms === undefined || category.data === undefined) {
      return;
    }
    const transformedData = category.data.map((datum) => {
      const transformedDatum = Object.assign({}, datum);
      category.transforms.forEach((transform) => {
        const methodInputs = transform.inputs.map((key) => datum[key]);
        transformedDatum[transform.key] = transform.method(methodInputs);
      });
      return transformedDatum;
    });
    category.data = transformedData;
  });

  const dataJSX: Record<string, Array<JSX.Element>> = {
    menuItems: [],
    routes: [],
  };

  // create JSX elements from categories
  dataCategories.forEach((category) => {
    let focusStyle = null;

    if (location?.pathname === category.to) {
      focusStyle = style.active;
    }
    dataJSX.menuItems.push({
      menuItem: (
        <MenuItem className={style.menuItem} key={category.text} as="div">
          <Link to={category.to}>
            <div className={style.category}>
              <div className={cx(style.title, focusStyle)}>{category.text}</div>
              <div className={style.count}>{category.data?.length}</div>
            </div>
          </Link>
        </MenuItem>
      ),
    });

    dataJSX.routes.push(
      <Route
        path={category.to}
        key={category.text}
        render={() => (
          <DataSubview data={category.data} headers={category.headers} />
        )}
      />
    );
  });

  return (
    <div className={style.dataRoot}>
      <div className={style.navigation}>
        <Tab
          className={style.menu}
          menu={TAB_MENU_OPTIONS}
          panes={dataJSX.menuItems}
        />
      </div>
      <div className={style.view}>
        <Switch>
          {dataJSX.routes}
          <Redirect from="/data" to="/data/samples" exact />
        </Switch>
      </div>
    </div>
  );
};

export default Data;
