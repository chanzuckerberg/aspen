import { DialogContentProps } from "@material-ui/core";
import React from "react";
import { StyledDialogContent } from "./style";

const DialogContent = (props: DialogContentProps): JSX.Element => {
  return <StyledDialogContent {...props} />;
};

export default DialogContent;
