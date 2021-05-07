interface BioinformaticsType {
  [index: string]: JSONPrimitive;
  type: "BioinformaticsType";
}

interface GISAID {
  status: "submitted" | "not_eligible" | "accepted" | "rejected" | "no_info";
  gisaid_id?: string;
}

interface Sample extends BioinformaticsType {
  type: "Sample";
  privateId: string;
  publicId: string;
  uploadDate: string;
  collectionDate: string;
  collectionLocation: string;
  gisaid: GISAID;
}

interface Tree extends BioinformaticsType {
  type: "Tree";
  id: number;
  name?: string;
  pathogenGenomeCount: number;
  dateCompleted: string;
  downloadLink?: string;
}

type BioinformaticsData = Sample | Tree;
