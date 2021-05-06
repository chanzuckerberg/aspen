/* eslint-disable react/display-name */

import { css } from "@emotion/css";
import { Tooltip } from "czifui";
import React from "react";
import { defaultHeaderRenderer } from "src/common/components/library/data_table";
import dataTableStyle from "src/common/components/library/data_table/index.module.scss";
import { createTableHeaderRenderer } from "src/common/utils";

const arrow = css`
  left: 0 !important;
`;

const LINEAGE_TOOLTIP_TEXT = (
  <div>
    <b>Lineage:</b> A lineage is a named group of related sequences. A few
    lineages have been associated with changes in the epidemiological or
    biological characteristics of the virus. We continually update these
    lineages based on the evolving Pangolin designations. Lineages determined by
    Pangolin. Learn more.
  </div>
);

const SampleRenderers: Record<string, HeaderRenderer> = {
  lineage: ({ header }): JSX.Element => (
    <div key={header.key} className={dataTableStyle.headerCell}>
      <Tooltip
        classes={{ arrow }}
        title={LINEAGE_TOOLTIP_TEXT}
        placement="bottom-start"
      >
        <div className={dataTableStyle.headerCellContent}>{header.text}</div>
      </Tooltip>
    </div>
  ),
};

export const SampleHeader = createTableHeaderRenderer(
  SampleRenderers,
  defaultHeaderRenderer
);
