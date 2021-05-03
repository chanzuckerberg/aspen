import React from "react";
import style from "./index.module.scss";

interface Props {
  numOfColumns: number;
}

const EmptyState = ({ numOfColumns }: Props): JSX.Element => {
  return (
    <div className={style.container}>
      <EmptyCells numOfColumns={numOfColumns} />
    </div>
  );
};

function EmptyCells({ numOfColumns = 0 }): JSX.Element {
  return (
    <>
      {Array.from(Array(numOfColumns)).map((_, index) => {
        return (
          <div key={index} className={style.cellContainer}>
            {index ? <div className={style.cell} /> : <FirstColumn />}
          </div>
        );
      })}
    </>
  );
}

function FirstColumn() {
  return (
    <div className={style.firstColumn}>
      <div className={style.square} />
      <div className={style.bars}>
        <div className={style.long} />
        <div className={style.short} />
      </div>
    </div>
  );
}

export { EmptyState };
