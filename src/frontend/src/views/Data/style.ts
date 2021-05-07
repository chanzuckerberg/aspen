import styled from "@emotion/styled";
import { fontBodyXxs, getColors } from "czifui";
import { pageContentHeight } from "src/common/styles/mixins/global";

export const Container = styled.div`
  ${pageContentHeight}

  display: flex;
  flex-flow: column wrap;
  align-content: flex-start;
`;

export const Subtext = styled.div`
  ${fontBodyXxs}
  ${(props) => {
    const colors = getColors(props);

    return `
      color: ${colors?.gray[400]};
    `;
  }}
`;

export const GISAIDCell = styled.div`
  flex-direction: column;
  align-items: unset;
`;
