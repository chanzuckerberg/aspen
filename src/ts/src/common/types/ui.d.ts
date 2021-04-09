interface ButtonInfo {
  content: string | JSX.Element;
  type: "primary" | "secondary";
  link: string | "cancel";
}

interface ModalInfo {
  header?: string | JSX.Element;
  body?: string | JSX.Element;
  buttons?: ButtonInfo[];
  width?: number;
  backgroundColor?: string;
}
