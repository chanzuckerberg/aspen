import React, { FC, useEffect, useState } from "react";
import { DEFAULT_FETCH_OPTIONS } from "src/common/api";
import { Button } from "src/common/components";
import { stripProtocol } from "../../urlUtils";

interface Props {
  treeId: string;
}

const ConfirmButton = (props: Props) => {
  const { treeId } = props;

  const [url, setUrl] = useState("");
  useEffect(() => {
    getUrl();

    async function getUrl() {
      setUrl(await getTreeUrl(treeId));
    }
  }, [treeId]);

  return (
    <Button {...props} link={url}>
      Confirm
    </Button>
  );
};

export const createConfirmButton = (treeId: string): FC => {
  const TempConfirmButton = (props: unknown) => (
    <ConfirmButton {...props} treeId={treeId} />
  );

  TempConfirmButton.displayName = "TempConfirmButton";

  return TempConfirmButton;
};

async function getTreeUrl(treeId: string) {
  const result = await fetch(
    `${process.env.API_URL}/api/auspice/view/${treeId}`,
    DEFAULT_FETCH_OPTIONS
  );

  const json = await result.json();

  const encodedJsonUrl = encodeURIComponent(stripProtocol(json.url));

  return "https://nextstrain.org/fetch/" + encodedJsonUrl;
}
