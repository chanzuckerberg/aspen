import styled from "@emotion/styled";
import { fontBodyXs, fontHeaderXs, getSpacings } from "czifui";

export const Wrapper = styled.div`
  display: flex;
  justify-content: space-between;
`;

export const Label = styled.span`
  ${fontHeaderXs}

  ${(props) => {
    const spacings = getSpacings(props);

    return `
      margin-right: ${spacings?.m}px;
    `;
  }}
`;

export const Text = styled.span`
  ${fontBodyXs}
`;
