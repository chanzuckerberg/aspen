/* eslint-disable react/display-name */

import React from "react";
import { Modal } from "src/common/components";
import { ReactComponent as ExternalLinkIcon } from "src/common/icons/ExternalLink.svg";
import { ReactComponent as TreeIcon } from "src/common/icons/PhyloTree.svg";
import { ReactComponent as SampleIcon } from "src/common/icons/Sample.svg";
import {
  createTableCellRenderer,
  createTreeModalInfo,
  stringGuard,
} from "src/common/utils";
import style from "./index.module.scss";

const DEFAULT_RENDERER = (value: JSONPrimitive): JSX.Element => {
  return <div className={style.cell}>{value}</div>;
};

const SAMPLE_CUSTOM_RENDERERS: Record<string | number, CellRenderer> = {
  privateId: (value: JSONPrimitive): JSX.Element => (
    <div className={style.cell}>
      {<SampleIcon className={style.icon} />}
      {value}
    </div>
  ),
};

const SampleRenderer = createTableCellRenderer(
  SAMPLE_CUSTOM_RENDERERS,
  DEFAULT_RENDERER
);

const TREE_CUSTOM_RENDERERS: Record<string | number, CellRenderer> = {
  downloadLink: (value: JSONPrimitive): JSX.Element => {
    const stringValue = stringGuard(value);
    return (
      <div className={style.cell}>
        <a href={stringValue} download>
          Download
        </a>
      </div>
    );
  },
  name: (value: JSONPrimitive): JSX.Element => {
    const stringValue = stringGuard(value);

    const treeID = stringValue.split(" ")[0];

    return (
      <Modal data={createTreeModalInfo(treeID)} className={style.cell}>
        {<TreeIcon className={style.icon} />}
        {stringValue}
        {<ExternalLinkIcon className={style.icon} />}
      </Modal>
    );
  },
};

const TreeRenderer = createTableCellRenderer(
  TREE_CUSTOM_RENDERERS,
  DEFAULT_RENDERER
);

export { SampleRenderer, TreeRenderer };
