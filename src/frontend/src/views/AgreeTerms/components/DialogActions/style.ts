import styled from "@emotion/styled";
import { DialogActions } from "@material-ui/core";
import { getSpacings } from "czifui";

export const StyledDialogActions = styled(DialogActions)`
  justify-content: flex-start;

  ${(props) => {
    const spacings = getSpacings(props);

    return `
      padding: 0 ${spacings?.xxl}px ${spacings?.xxl}px ${spacings?.xxl}px;
    `;
  }}
`;
