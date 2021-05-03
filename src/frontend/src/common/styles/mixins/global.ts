import { css } from "@emotion/react";
import { NAV_BAR_HEIGHT_PX } from "src/components/NavBar";

export const pageContentHeight = css`
  height: calc(100% - ${NAV_BAR_HEIGHT_PX}px);
`;
