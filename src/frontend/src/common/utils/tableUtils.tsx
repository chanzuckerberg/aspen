import { memoize } from "lodash/fp";
import { ModalInfo } from "../types/ui";
import { createConfirmButton } from "./TreeModal/ConfirmButton";

/* eslint-disable react/display-name */

const UNDEFINED_TEXT = "---";

export function createTableCellRenderer(
  customRenderers: Record<string, CellRenderer>,
  defaultRenderer: CellRenderer
): CustomRenderer {
  return ({ header, value, item, index }: CustomTableRenderProps) => {
    const unwrappedValue = value || UNDEFINED_TEXT;

    const renderer = customRenderers[header.key] || defaultRenderer;

    return renderer({
      header,
      index,
      item,
      value: unwrappedValue,
    });
  };
}

export function createTableHeaderRenderer(
  customRenderers: Record<string, HeaderRenderer>,
  defaultRenderer: HeaderRenderer
): CustomRenderer {
  return ({ header, index }: CustomTableRenderProps): JSX.Element => {
    const renderer = customRenderers[header.key] || defaultRenderer;

    return renderer({
      header,
      index,
    });
  };
}

export const createTreeModalInfo = memoize(createTreeModalInfo_);

function createTreeModalInfo_(treeId: string): ModalInfo {
  return {
    body:
      "You are leaving Aspen and sending your data to a private visualization on auspice.us, which is not controlled by Aspen.",
    buttons: [
      {
        Button: createConfirmButton(treeId),
      },
      {
        content: "Cancel",
        link: "cancel",
        type: "secondary",
      },
    ],
    header:
      "Please confirm you're ready to send your data to Auspice to see your tree.",
  };
}
