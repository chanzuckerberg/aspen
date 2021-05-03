import { Button, createStyles } from "@material-ui/core";
import { ExpandMore } from "@material-ui/icons";
import { makeStyles } from "@material-ui/styles";
import { AppThemeOptions, Menu, MenuItem } from "czifui";
import React from "react";
import { Link } from "react-router-dom";
import { API } from "src/common/api";
import { ROUTES } from "src/common/routes";

const useStyles = makeStyles((theme: AppThemeOptions) => {
  const palette = theme.palette;

  return createStyles({
    text: {
      color: palette?.common?.white,
    },
  });
});

interface UserMenuProps {
  user: string;
}

const UserMenu = ({ user }: UserMenuProps): JSX.Element => {
  const [anchorEl, setAnchorEl] = React.useState<Element | null>(null);

  const classes = useStyles();

  const handleClick: React.MouseEventHandler<HTMLButtonElement> = (event) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  return (
    <>
      <Button onClick={handleClick} classes={classes} endIcon={<ExpandMore />}>
        {user}
      </Button>
      <Menu
        anchorEl={anchorEl}
        keepMounted
        open={Boolean(anchorEl)}
        onClose={handleClose}
        getContentAnchorEl={null}
      >
        <a href={ROUTES.CONTACT_US_EMAIL} target="_blank" rel="noopener">
          <MenuItem onClick={handleClose}>Contact us</MenuItem>
        </a>
        <Link to={ROUTES.TERMS} target="_blank" rel="noopener">
          <MenuItem onClick={handleClose}>Terms of Use</MenuItem>
        </Link>
        <Link to={ROUTES.PRIVACY} target="_blank" rel="noopener">
          <MenuItem onClick={handleClose}>Privacy Policy</MenuItem>
        </Link>
        <a href={process.env.API_URL + API.LOG_OUT}>
          <MenuItem onClick={handleClose}>Logout</MenuItem>
        </a>
      </Menu>
    </>
  );
};

export default UserMenu;
