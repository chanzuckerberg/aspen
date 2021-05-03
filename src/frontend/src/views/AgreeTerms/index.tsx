import { Dialog } from "@material-ui/core";
import { Button, Link, List, ListItem, ListSubheader } from "czifui";
import React, { useEffect, useState } from "react";
import { logout, updateUserData } from "src/common/api";
import { ROUTES } from "src/common/routes";
import DialogActions from "./components/DialogActions";
import DialogContent from "./components/DialogContent";
import DialogTitle from "./components/DialogTitle";
import { Container, Details, Title } from "./style";

export default function AgreeTerms(): JSX.Element {
  const [isLoading, setIsLoading] = useState(false);
  const [shouldRedirect, setShouldRedirect] = useState(false);
  const [hasAcceptedTerms, setHasAcceptedTerms] = useState(false);

  useEffect(() => {
    if (shouldRedirect) {
      window.location.href = process.env.PUBLIC_URL + ROUTES.DATA;
    }
  }, [shouldRedirect]);

  useEffect(() => {
    if (!hasAcceptedTerms) return;

    agreeTos();

    async function agreeTos() {
      setIsLoading(true);
      await updateUserData({ agreed_to_tos: true });
      setShouldRedirect(true);
    }
  }, [hasAcceptedTerms]);

  function handleAcceptClick() {
    setHasAcceptedTerms(true);
  }

  async function handleDeclineClick() {
    setIsLoading(true);
    try {
      await logout();
    } catch {
      setIsLoading(false);
    }
    setIsLoading(false);
  }

  return (
    <Container>
      <Dialog open>
        <DialogTitle>
          <Title>
            First, a note about how we protect and handle your data.
          </Title>
        </DialogTitle>
        <DialogContent>
          <List>
            <ListSubheader disableSticky>
              We take data privacy and security very seriously. Here are a few
              key things to know:
            </ListSubheader>
            <ListItem fontSize="s">
              You always own and control the data you upload.
            </ListItem>
            <ListItem fontSize="s">
              Only other members of your group can see your data. CDPH can see
              samples, but not your private, internal identifiers.
            </ListItem>
            <ListItem fontSize="s">
              New sequences will be automatically submitted to GISAID two weeks
              after upload.
            </ListItem>
            <ListItem fontSize="s">
              You can mark a sample as “private” anytime during the first two
              weeks after upload. “Private” samples are not shared with CDPH or
              GISAID, but are visible to your group.{" "}
            </ListItem>
            <ListItem fontSize="s">
              Aspen does not contain any personally identifiable information or
              protected health information.
            </ListItem>
            <ListItem fontSize="s">
              We utilize industry standard best practices in information
              security, such as encrypting your data at rest and in transit, to
              ensure the security of your data.
            </ListItem>
            <Details>
              Take a look at our full{" "}
              <Link href={ROUTES.TERMS} target="_blank" rel="noopener">
                Terms of Service
              </Link>{" "}
              and{" "}
              <Link href={ROUTES.PRIVACY} target="_blank" rel="noopener">
                Privacy Policy
              </Link>
              . We’ve put together an{" "}
              <Link href={ROUTES.FAQ} target="_blank" rel="noopener">
                FAQ
              </Link>{" "}
              to make these easier to understand. Please{" "}
              <Link
                href={ROUTES.CONTACT_US_EMAIL}
                target="_blank"
                rel="noopener"
              >
                get in touch
              </Link>{" "}
              if you have any questions or concerns, we’re here to help.
            </Details>
          </List>
        </DialogContent>
        <DialogActions>
          <Button
            disabled={isLoading}
            color="primary"
            variant="contained"
            isRounded
            autoFocus
            onClick={handleAcceptClick}
          >
            Accept
          </Button>
          <Button
            disabled={isLoading}
            color="primary"
            variant="outlined"
            isRounded
            onClick={handleDeclineClick}
          >
            Decline
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
}
