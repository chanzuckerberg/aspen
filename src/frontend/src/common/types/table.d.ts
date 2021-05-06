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

type CustomRenderer = ({
  header,
  value,
  item,
  index,
}: CustomTableRenderProps) => JSX.Element;

type CellRendererProps = Omit<CustomTableRenderProps, "header">;

type CellRenderer = ({ value, item, index }: CellRendererProps) => JSX.Element;

type HeaderRendererProps = Omit<CustomTableRenderProps, "item", "value">;

type HeaderRenderer = ({ header, idex }: HeaderRendererProps) => JSX.Element;
