/* eslint-disable react/display-name */

const UNDEFINED_TEXT = "---";

function createTableCellRenderer(
  customRenderers: Record<string | number, CellRenderer>,
  defaultRenderer: CellRenderer
): CustomRenderer {
  return ({ header, value, item, index }: CustomTableRenderProps) => {
    let unwrappedValue;
    if (value === undefined) {
      unwrappedValue = UNDEFINED_TEXT;
    } else {
      unwrappedValue = value;
    }

    if (customRenderers[header.key] !== undefined) {
      const cellRenderFunction = customRenderers[header.key];
      return cellRenderFunction(unwrappedValue, item, index);
    }

    return defaultRenderer(unwrappedValue, item, index);
  };
}

function createTreeModalInfo(link: string): ModalInfo {
  return {
    body:
      "You are leaving Aspen and sending your data to a private visualization on auspice.us, which is not controlled by Aspen.",
    buttons: [
      {
        content: "Confirm",
        link: link,
        type: "primary",
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

export { createTableCellRenderer, createTreeModalInfo };
