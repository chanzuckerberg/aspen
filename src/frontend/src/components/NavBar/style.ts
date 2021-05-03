import styled from "@emotion/styled";
import { getSpacings } from "czifui";
import { Link } from "react-router-dom";

export const Logo = styled.img`
  width: 60px;

  ${(props) => {
    const spacings = getSpacings(props);

    return `
      margin-right: ${spacings?.l}px;
    `;
  }}
`;

export const LogoAnchor = styled(Link)`
  display: flex;
  align-items: center;
  justify-content: center;
`;
