import styled from "@emotion/styled";
import { getColors, getSpacings } from "czifui";

export const TableRow = styled.div`
  display: flex;
  border-bottom: 1px solid rgba(0, 0, 0, 0.1);

  ${(props) => {
    const colors = getColors(props);

    return `
      &:hover {
        background-color: ${colors?.primary[100]};
      }
    `;
  }}
`;

export const RowContent = styled.div`
  display: flex;
  align-items: center;
  width: 100%;
  ${(props) => {
    const spacings = getSpacings(props);

    return `
      padding: ${spacings?.l}px 0;
    `;
  }}
`;
