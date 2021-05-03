import styled from "@emotion/styled";
import {
  AppThemeOptions,
  fontBodyM,
  fontBodyS,
  fontBodyXs,
  fontHeaderXxl,
  getColors,
  getShadows,
  getSpacings,
} from "czifui";
import { pageContentHeight } from "src/common/styles/mixins/global";

export const Container = styled.div`
  ${pageContentHeight}

  display: flex;
  flex-direction: column;
`;

export const CardContainer = styled.div`
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
`;

export const Card = styled.div`
  display: flex;
  flex-direction: column;

  ${(props) => {
    const shadows = getShadows(props);
    const spacings = getSpacings(props);

    return `
      height: 360px;
      width: 400px;
      padding: ${spacings?.xxl}px ${spacings?.xl}px ${spacings?.xxl}px ${spacings?.xxl}px;
      box-shadow: ${shadows?.s};
    `;
  }}
`;

export const Left = styled.div`
  display: flex;
  flex-direction: column;

  /* (thuang): fill up remaining horizontal space */
  flex: 1;
`;

export const Right = styled.div`
  width: 70px;
  height: 70px;
`;

export const Title = styled.div`
  ${fontHeaderXxl}
  ${marginBottom}
`;

export const Content = styled.div`
  /* (thuang): fill up remaining vertical space */
  flex: 1;
  display: flex;

  ${fontBodyM}

  ${(props) => {
    const spacings = getSpacings(props);

    return `
      margin-bottom: ${spacings?.xl}px;
    `;
  }}
`;

export const Main = styled.div`
  ${fontBodyM}
  ${marginBottom}
`;

export const Details = styled.div`
  ${fontBodyS}

  ${(props) => {
    const colors = getColors(props);

    return `
      color: ${colors?.gray[500]};
    `;
  }}
`;

export const ButtonContainer = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
`;

export const Virus = styled.img`
  width: 65px;
  height: 65px;
`;

export const Footer = styled.div`
  height: 76px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

export const FooterButtonContainer = styled.div`
  ${fontBodyXs}

  width: 260px;
  display: flex;
  justify-content: space-between;

  ${(props) => {
    const colors = getColors(props);

    return `
      &> a {
        color: ${colors?.gray[600]}
      }
    `;
  }}
`;

function marginBottom(props: { theme?: AppThemeOptions }) {
  const spacings = getSpacings(props);

  return `
      margin-bottom: ${spacings?.s}px;
    `;
}
