/* eslint-disable react/display-name */

import React from "react";
import { Modal } from "src/common/components";
import { defaultCellRenderer } from "src/common/components/library/data_table";
import dataTableStyle from "src/common/components/library/data_table/index.module.scss";
import { ReactComponent as ExternalLinkIcon } from "src/common/icons/ExternalLink.svg";
import { ReactComponent as TreeIcon } from "src/common/icons/PhyloTree.svg";
import { ReactComponent as SampleIcon } from "src/common/icons/Sample.svg";
import {
  createTableCellRenderer,
  createTreeModalInfo,
  stringGuard,
} from "src/common/utils";

const SAMPLE_CUSTOM_RENDERERS: Record<string | number, CellRenderer> = {
  // DEBUG
  // DEBUG
  // DEBUG
  // DEBUG
  // DEBUG
  // DEBUG
  // REMOVE BEFORE PR
  gisaid: () => <div></div>,
  lineage: ({ value }): JSX.Element => (
    <div className={dataTableStyle.cell}>{value.lineage}</div>
  ),
  privateId: ({ value }): JSX.Element => (
    <div className={dataTableStyle.cell}>
      {<SampleIcon className={dataTableStyle.icon} />}
      {value}
    </div>
  ),
};

const SampleRenderer = createTableCellRenderer(
  SAMPLE_CUSTOM_RENDERERS,
  defaultCellRenderer
);

const TREE_CUSTOM_RENDERERS: Record<string | number, CellRenderer> = {
  downloadLink: ({ value }): JSX.Element => {
    const stringValue = stringGuard(value);
    return (
      <div className={dataTableStyle.cell}>
        <a href={stringValue} download>
          Download
        </a>
      </div>
    );
  },
  name: ({ value }): JSX.Element => {
    const stringValue = stringGuard(value);

    const treeID = stringValue.split(" ")[0];
    return (
      <Modal data={createTreeModalInfo(treeID)} className={dataTableStyle.cell}>
        {<TreeIcon className={dataTableStyle.icon} />}
        {stringValue}
        {<ExternalLinkIcon className={dataTableStyle.icon} />}
      </Modal>
    );
  },
};

const TreeRenderer = createTableCellRenderer(
  TREE_CUSTOM_RENDERERS,
  defaultCellRenderer
);

export { SampleRenderer, TreeRenderer };
