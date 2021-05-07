export const TREE_TRANSFORMS: Transform[] = [
  {
    inputs: ["id", "creationDate"],
    key: "name",
    method: (inputs: (number | string)[]): string => {
      // temporary until we use ISO 8601
      if (typeof inputs[1] !== "string") {
        return `${inputs[0]} Ancestors ??????`;
      }
      const re = /\d\d(\d\d)-(\d\d)-(\d\d)/;
      const matchArray = re.exec(inputs[1]);
      if (matchArray === null) {
        return `${inputs[0]} Ancestors ??????`;
      }
      return `${inputs[0]} Ancestors ${matchArray[1]}${matchArray[2]}${matchArray[3]}`;
    },
  },
  {
    inputs: ["id"],
    key: "downloadLink",
    method: (inputs: number[]): string | undefined => {
      const id = inputs[0];
      if (typeof id !== "number") {
        return undefined;
      }
      return `${process.env.API_URL}/api/phylo_tree/${id}`;
    },
  },
  {
    inputs: ["id"],
    key: "accessionsLink",
    method: (inputs: number[]): string | undefined => {
      const id = inputs[0];
      if (typeof id !== "number") {
        return undefined;
      }
      return `${process.env.API_URL}/api/phylo_tree/sample_ids/${id}`;
    },
  },
];
