interface Transform {
  key: string;
  inputs: string[];
  method: (inputs: any[]) => any; // eslint-disable-line @typescript-eslint/no-explicit-any
}
