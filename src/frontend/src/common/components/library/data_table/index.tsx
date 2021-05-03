import React, { FunctionComponent } from "react";
import AutoSizer from "react-virtualized-auto-sizer";
import { FixedSizeList, ListChildComponentProps } from "react-window";
import { EmptyState } from "../data_subview/components/EmptyState";
import style from "./index.module.scss";

interface Props {
  data?: TableItem[];
  headers: Header[];
  renderer?: CustomRenderer;
  isLoading: boolean;
}

// (thuang): If item height changes, we need to update this value!
const ITEM_HEIGHT_PX = 60;

const LOADING_STATE_ROW_COUNT = 10;

const UNDEFINED_TEXT = "---";

function defaultCellRenderer({ value }: CustomTableRenderProps): JSX.Element {
  let displayData;
  if (value === undefined) {
    displayData = UNDEFINED_TEXT;
  } else {
    displayData = value;
  }
  return <div className={style.cell}>{displayData}</div>;
}

const DataTable: FunctionComponent<Props> = ({
  data = [],
  headers,
  renderer = defaultCellRenderer,
  isLoading,
}: Props) => {
  const indexingKey = headers[0].key;

  // render functions
  const headerRow = headers.map((column: Header) => (
    <div key={column.key} className={style.headerCell}>
      <div className={style.headerCellContent}>{column.text}</div>
    </div>
  ));

  const sampleRow = (item: TableItem): React.ReactNode => {
    if (isLoading) {
      return <EmptyState numOfColumns={headers.length} />;
    }

    return headers.map((header, index) => {
      const value = item[header.key];

      return (
        <div
          key={`${item[indexingKey]}-${header.key}`}
          className={style.rowContent}
        >
          {renderer({ header, index, item, value })}
        </div>
      );
    });
  };

  function renderRow(props: ListChildComponentProps) {
    const item = data[props.index];

    return (
      <div className={style.tableRow} style={props.style}>
        {sampleRow(item)}
      </div>
    );
  }

  return (
    <div className={style.container}>
      <div className={style.header}>{headerRow}</div>
      <div className={style.tableContent}>
        <AutoSizer>
          {({ height, width }) => {
            return (
              <FixedSizeList
                height={height}
                itemData={data}
                itemCount={isLoading ? LOADING_STATE_ROW_COUNT : data.length}
                itemSize={ITEM_HEIGHT_PX}
                width={width}
              >
                {renderRow}
              </FixedSizeList>
            );
          }}
        </AutoSizer>
      </div>
    </div>
  );
};

export { DataTable };
