import React, { FunctionComponent } from "react";
import AutoSizer from "react-virtualized-auto-sizer";
import { FixedSizeList, ListChildComponentProps } from "react-window";
import { EmptyState } from "../data_subview/components/EmptyState";
import style from "./index.module.scss";
import { TableRow } from "./style";

interface Props {
  data?: TableItem[];
  headers: Header[];
  isLoading: boolean;
  renderer?: CustomRenderer;
  headerRenderer?: HeaderRenderer;
}

// (thuang): If item height changes, we need to update this value!
const ITEM_HEIGHT_PX = 60;

const LOADING_STATE_ROW_COUNT = 10;

const UNDEFINED_TEXT = "---";

export function defaultCellRenderer({ value }: CellRendererProps): JSX.Element {
  const displayData = value || UNDEFINED_TEXT;

  return <div className={style.cell}>{displayData}</div>;
}

export function defaultHeaderRenderer({
  header,
}: HeaderRendererProps): JSX.Element {
  return (
    <div key={header.key} className={style.headerCell}>
      <div className={style.headerCellContent}>{header.text}</div>
    </div>
  );
}

export const DataTable: FunctionComponent<Props> = ({
  data = [],
  headers,
  headerRenderer = defaultHeaderRenderer,
  renderer = defaultCellRenderer,
  isLoading,
}: Props) => {
  const indexingKey = headers[0].key;

  // render functions
  const headerRow = headers.map((header: Header, index) =>
    headerRenderer({ header, index })
  );

  const sampleRow = (item: TableItem): React.ReactNode => {
    if (isLoading) {
      return <EmptyState numOfColumns={headers.length} />;
    }

    return headers.map((header, index) => {
      // DEBUG
      // DEBUG
      // DEBUG
      // DEBUG
      // DEBUG
      // DEBUG
      // MOCK LINEAGE DATA
      const value = item[header.key] || {
        last_updated: "2021-01-11",
        lineage: "B.1.1.7",
        probability: "1.0",
        version: "2021-01-11",
      };

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

    return <TableRow style={props.style}>{sampleRow(item)}</TableRow>;
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
