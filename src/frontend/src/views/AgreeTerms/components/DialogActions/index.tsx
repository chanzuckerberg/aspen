import { DialogActionsProps } from "@material-ui/core";
import React from "react";
import { StyledDialogActions } from "./style";

const DialogActions = (props: DialogActionsProps): JSX.Element => {
  return <StyledDialogActions {...props} />;
};

export default DialogActions;
