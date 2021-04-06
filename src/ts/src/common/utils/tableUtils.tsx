import React from "react";

const UNDEFINED_TEXT = "---";

function createTableCellRenderer(
    customRenderers: Record<string | number, CellRenderer>,
    defaultRenderer: CellRenderer,
): CustomRenderer {
    const renderer: CustomRenderer = ({
        header,
        value,
        item,
        index
    }: CustomTableRenderProps) => {
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
    return renderer;
}

export { createTableCellRenderer };