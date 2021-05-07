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
} from "src/common/utils";
import { GISAIDCell, Subtext } from "./style";
import { GISAID_STATUS_TO_TEXT } from "./utils/samples";

const DEFAULT_RENDERER = (value: JSONPrimitive): JSX.Element => {
  return <div className={dataTableStyle.cell}>{value}</div>;
};

const SAMPLE_CUSTOM_RENDERERS: Record<string | number, CellRenderer> = {
  gisaid(value): JSX.Element {
    const { gisaid_id, status } = (value as unknown) as Sample["gisaid"];

    return (
      <GISAIDCell className={dataTableStyle.cell}>
        {GISAID_STATUS_TO_TEXT[status]}
        {gisaid_id && <Subtext>{gisaid_id}</Subtext>}
      </GISAIDCell>
    );
  },
  privateId(value: JSONPrimitive): JSX.Element {
    return (
      <div className={dataTableStyle.cell}>
        {<SampleIcon className={dataTableStyle.icon} />}
        {value}
      </div>
    );
  },
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
  DEFAULT_RENDERER
);

export { SampleRenderer, TreeRenderer };
