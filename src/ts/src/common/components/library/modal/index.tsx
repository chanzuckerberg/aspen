import cx from "classnames";
import React, { FunctionComponent, useReducer } from "react";
import { Button } from "src/common/components";
import style from "./index.module.scss";

interface Props {
  data: ModalInfo;
  className: string;
  customStyle?: Stylesheet;
}

interface ModalState {
  displayModal: boolean;
}

function modalReducer(state: ModalState, action: ModalState): ModalState {
  return { ...state, ...action };
}

const Modal: FunctionComponent<Props> = ({
  data,
  className,
  customStyle,
  children,
}): JSX.Element => {
  const [state, dispatch] = useReducer(modalReducer, { displayModal: false });

  const closeModal = () => dispatch({ displayModal: false });

  function renderButtons(
    buttonInfo: ButtonInfo[] | undefined
  ): JSX.Element | null {
    if (buttonInfo === undefined || buttonInfo.length < 1) {
      return null;
    }

    const buttons = buttonInfo.map((button, index) => {
      let link: string | undefined = button.link;
      let onClick: (() => void) | undefined = undefined;

      if (link === "cancel") {
        link = undefined;
        onClick = closeModal;
      }

      return (
        <Button link={link} type={button.type} onClick={onClick} key={index}>
          {button.content}
        </Button>
      );
    });

    return <React.Fragment>{buttons}</React.Fragment>;
  }

  function renderElements(state: ModalState): JSX.Element | null {
    if (!state.displayModal) return null;

    return (
      <React.Fragment>
        <div
          className={cx(style.background, customStyle?.background)}
          onClick={closeModal}
        ></div>
        <div className={cx(style.modal, customStyle?.modal)}>
          <div className={style.content}>
            <div className={style.header}>{data.header}</div>
            <div className={style.body}>{data.body}</div>
            <div className={style.buttons}>{renderButtons(data.buttons)}</div>
          </div>
        </div>
      </React.Fragment>
    );
  }

  const childrenWithTrigger = (children: React.ReactNode) => {
    return React.Children.map(children, (child) => (
      <span
        className={style.children}
        onClick={() => dispatch({ displayModal: true })}
      >
        {child}
      </span>
    ));
  };

  return (
    <React.Fragment>
      <div className={className}>{childrenWithTrigger(children)}</div>
      {renderElements(state)}
    </React.Fragment>
  );
};

export { Modal };
