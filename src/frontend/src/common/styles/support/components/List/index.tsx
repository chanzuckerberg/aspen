import { List as RawList, ListItem } from "czifui";
import React from "react";

interface Props {
  items: React.ReactNode[];
  ordered?: boolean;
}

const List = ({ items, ordered }: Props): JSX.Element => {
  return (
    <RawList ordered={ordered}>
      {items.map((item, index) => {
        return (
          <ListItem ordered={ordered} key={index}>
            {item}
          </ListItem>
        );
      })}
    </RawList>
  );
};

export default List;
