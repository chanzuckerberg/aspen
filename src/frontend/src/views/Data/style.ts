import styled from "@emotion/styled";
import { pageContentHeight } from "src/common/styles/mixins/global";

export const Container = styled.div`
  ${pageContentHeight}

  display: flex;
  flex-flow: column wrap;
  align-content: flex-start;
`;
