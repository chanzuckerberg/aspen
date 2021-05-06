import styled from "@emotion/styled";
import {
  fontBodyS,
  fontBodyXxs,
  fontHeaderM,
  fontHeaderXl,
  fontHeaderXxl,
  getColors,
  getFontWeights,
} from "czifui";

export const NarrowContainer = styled.div`
  max-width: 800px;
  margin: 90px auto;
`;

export const B = styled.b`
  ${(props) => {
    const fontWeights = getFontWeights(props);

    return `
      font-weight: ${fontWeights?.semibold};
    `;
  }}
`;

export const H1 = styled.h1`
  ${fontHeaderXxl}

  margin-bottom: 0;
  position: relative;
`;

export const H2 = styled.h2`
  ${fontHeaderXl}

  margin-top: 40px;
  position: relative;
`;

export const H3 = styled.h3`
  ${fontHeaderM}

  margin-top: 30px;
  position: relative;
`;

export const Number = styled.span`
  position: absolute;
  right: 100%;
  margin-right: 8px;
`;

export const H4 = styled.h4`
  ${fontBodyXxs}

  margin-top: 5px;

  ${(props) => {
    const colors = getColors(props);

    return `
      color: ${colors?.gray[500]};
    `;
  }}
`;

export const P = styled.p`
  ${fontBodyS}
`;

export const Title = styled.div`
  margin-bottom: 50px;
`;
