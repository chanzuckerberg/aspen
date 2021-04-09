import React, { FunctionComponent } from "react";
import { Table } from "semantic-ui-react";
import style from "./index.module.scss";

interface Props {
  data?: TableItem[];
  headers: Header[];
  renderer?: CustomRenderer;
}

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
  renderer,
}: Props) => {
  const indexingKey = headers[0].key;

  // render functions
  const headerRow = headers.map((column: Header) => (
    <Table.HeaderCell key={column.key} className={style.headerCell}>
      <div className={style.headerCellContent}>{column.text}</div>
    </Table.HeaderCell>
  ));

  const sampleRow = (item: TableItem): Array<JSX.Element> => {
    return headers.map((header, index) => {
      const value = item[header.key];
      if (renderer === undefined) {
        renderer = defaultCellRenderer;
      }
      return (
        <Table.Cell key={`${item[indexingKey]}-${header.key}`}>
          {renderer({ header, index, item, value })}
        </Table.Cell>
      );
    });
  };

  function tableRows(data: TableItem[]): Array<JSX.Element> {
    return data.map((item) => (
      <Table.Row key={`${item[indexingKey]}`}>{sampleRow(item)}</Table.Row>
    ));
  }

  return (
    <Table basic="very">
      <Table.Header className={style.header}>
        <Table.Row>{headerRow}</Table.Row>
      </Table.Header>
      <Table.Body>{tableRows(data)}</Table.Body>
    </Table>
  );
};

export { DataTable };
