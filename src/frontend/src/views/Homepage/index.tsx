import { Button } from "czifui";
import React from "react";
import { Link } from "react-router-dom";
import { API } from "src/common/api";
import { ROUTES } from "src/common/routes";
import ConsensusGenomes from "./ConsensusGenomes.svg";
import {
  ButtonContainer,
  Card,
  CardContainer,
  Container,
  Content,
  Details,
  Footer,
  FooterButtonContainer,
  Left,
  Main,
  Right,
  Title,
  Virus,
} from "./style";

export default function Homepage(): JSX.Element {
  return (
    <Container>
      <CardContainer>
        <Card>
          <Content>
            <Left>
              <Title>Welcome to Aspen!</Title>
              <Main>
                Aspen is a new tool that helps you manage, analyze and share
                your pathogen data for genomic epidemiology.
              </Main>
              <Details>
                This is also where you’ll receive all of your sequencing results
                from the COVIDTracker project at the CZBiohub.
              </Details>
            </Left>

            <Right>
              <Virus src={String(ConsensusGenomes)} />
            </Right>
          </Content>

          <ButtonContainer>
            <a href={process.env.API_URL + API.LOG_IN}>
              <Button isRounded color="primary" variant="contained">
                Sign in
              </Button>
            </a>
          </ButtonContainer>
        </Card>
      </CardContainer>
      <Footer>
        <FooterButtonContainer>
          <a href={ROUTES.CONTACT_US_EMAIL} target="_blank" rel="noopener">
            Contact
          </a>
          <Link to={ROUTES.TERMS} target="_blank" rel="noopener">
            Terms
          </Link>
          <Link to={ROUTES.PRIVACY} target="_blank" rel="noopener">
            Privacy
          </Link>
        </FooterButtonContainer>
      </Footer>
    </Container>
  );
}
