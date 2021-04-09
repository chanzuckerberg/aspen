import cx from "classnames";
import React, { FunctionComponent } from "react";
import style from "./index.module.scss";

interface Props {
  link?: string;
  type?: "primary" | "secondary";
  onClick?: () => void;
}

const buttonStyles: Record<string, string> = {
  primary: style.primary,
  secondary: style.secondary,
};

const Button: FunctionComponent<Props> = ({
  link,
  type = "primary",
  onClick,
  children,
}): JSX.Element => {
  const buttonElements = (
    <div className={cx(style.button, buttonStyles[type])} onClick={onClick}>
      <div className={style.text}>{children}</div>
    </div>
  );
  if (link === undefined) {
    return buttonElements;
  }
  return <a href={link}>{buttonElements}</a>;
};

export { Button };
