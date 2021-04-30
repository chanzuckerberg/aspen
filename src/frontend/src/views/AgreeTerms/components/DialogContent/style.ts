import styled from "@emotion/styled";
import { DialogContent } from "@material-ui/core";
import { getSpacings } from "czifui";

export const StyledDialogContent = styled(DialogContent)`
  ${(props) => {
    const spacings = getSpacings(props);

    return `
    padding: 0 ${spacings?.xxl}px ${spacings?.xl}px ${spacings?.xxl}px;
    `;
  }}
`;
