interface Header {
  [index: string]: string;
  text: string;
  key: string | number;
}

type TableItem = Record<string | number, JSONPrimitive>;

interface CustomTableRenderProps {
  header: Header;
  value: JSONPrimitive | undefined;
  item: TableItem;
  index: number;
}

interface CustomRenderer extends FunctionComponent<CustomTableRenderProps> {
  ({ header, value, item, index }): JSX.Element;
}

type CellRenderer = (
  value: JSONPrimitive,
  item: TableItem,
  index: number
) => JSX.Element;
