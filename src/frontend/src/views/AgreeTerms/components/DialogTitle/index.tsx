import { DialogTitleProps } from "@material-ui/core";
import React from "react";
import { StyledDialogTitle } from "./style";

const DialogTitle = (props: DialogTitleProps): JSX.Element => {
  return <StyledDialogTitle {...props} />;
};

export default DialogTitle;
