/* eslint-disable react/display-name */

import React from "react";
import { Modal } from "src/common/components";
import dataTableStyle from "src/common/components/library/data_table/index.module.scss";
import { ReactComponent as ExternalLinkIcon } from "src/common/icons/ExternalLink.svg";
import { ReactComponent as TreeIcon } from "src/common/icons/PhyloTree.svg";
import { ReactComponent as SampleIcon } from "src/common/icons/Sample.svg";
import {
  createTableCellRenderer,
  createTreeModalInfo,
  stringGuard,
  stripProtocol,
} from "src/common/utils";

const DEFAULT_RENDERER = (value: JSONPrimitive): JSX.Element => {
  return <div className={dataTableStyle.cell}>{value}</div>;
};

const SAMPLE_CUSTOM_RENDERERS: Record<string | number, CellRenderer> = {
  privateId: (value: JSONPrimitive): JSX.Element => (
    <div className={dataTableStyle.cell}>
      {<SampleIcon className={dataTableStyle.icon} />}
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
      <div className={dataTableStyle.cell}>
        <a href={stringValue} download>
          Download
        </a>
      </div>
    );
  },
  name: (value: JSONPrimitive): JSX.Element => {
    const stringValue = stringGuard(value);
    const treeID = stringValue.split(" ")[0];
    const treeLocation = `${stripProtocol(
      process.env.API_URL
    )}/api/auspice/view/${treeID}`;
    return (
      <Modal
        data={createTreeModalInfo(
          `https://nextstrain.org/fetch/${treeLocation}`
        )}
        className={dataTableStyle.cell}
      >
        {<TreeIcon className={dataTableStyle.icon} />}
        {stringValue}
        {<ExternalLinkIcon className={dataTableStyle.icon} />}
      </Modal>
    );
  },
};

const TreeRenderer = createTableCellRenderer(
  TREE_CUSTOM_RENDERERS,
  DEFAULT_RENDERER
);

export { SampleRenderer, TreeRenderer };
