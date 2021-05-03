import styled from "@emotion/styled";
import { DialogTitle } from "@material-ui/core";
import { getSpacings } from "czifui";

export const StyledDialogTitle = styled(DialogTitle)`
  ${(props) => {
    const spacings = getSpacings(props);

    return `
      padding: ${spacings?.xxl}px ${spacings?.xxl}px ${spacings?.xl}px ${spacings?.xxl}px;
    `;
  }}
`;
