import React from "react";
import { Label, Text, Wrapper } from "./style";

export interface Lineage {
  last_updated: string;
  lineage: string;
  probability: string;
  version: string;
}

interface Props {
  lineage: Lineage;
}

const DISPLAY_ORDER: Array<keyof Lineage> = [
  "lineage",
  "probability",
  "version",
  "last_updated",
];

export const LineageTooltip = ({ lineage }: Props): JSX.Element => {
  return (
    <>
      {DISPLAY_ORDER.map((key) => {
        const value = lineage[key];
        return <Row key={key} label={key as keyof Lineage} text={value} />;
      })}
    </>
  );
};

const KEY_TO_LABELS = {
  last_updated: "Last Updated",
  lineage: "Lineage",
  probability: "Probability",
  version: "PangoLEARN Version",
};

function Row({ label, text }: { label: keyof Lineage; text: string }) {
  return (
    <Wrapper>
      <Label>{KEY_TO_LABELS[label]}:</Label> <Text>{text}</Text>
    </Wrapper>
  );
}
