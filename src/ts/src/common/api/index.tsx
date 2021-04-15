// refactor as needed
import axios from "axios";
import { jsonToType } from "src/common/utils";

export const DEFAULT_FETCH_OPTIONS: RequestInit = {
  credentials: "include",
};

/** Generic functions to interface with the backend API **/

const API_KEY_TO_TYPE: Record<string, string> = {
  group: "Group",
  phylo_trees: "Tree",
  samples: "Sample",
  user: "User",
};

function convert<U extends APIResponse, T extends U[keyof U]>(
  entry: Record<string, JSONPrimitive>,
  keyMap: Map<string, string | number> | null,
  key: keyof U
): T {
  const converted = jsonToType<T>(entry, keyMap);
  // key should always be a string anyways. no funky business please.
  converted.type = API_KEY_TO_TYPE[String(key)];

  return converted;
}

async function apiResponse<T extends APIResponse>(
  keys: (keyof T)[],
  mappings: (Map<string, string | number> | null)[],
  endpoint: string
): Promise<T> {
  const response = await axios.get(process.env.API_URL + endpoint, {
    withCredentials: true,
  });
  const convertedData = keys.map((key, index) => {
    type keyType = T[typeof key];
    const typeData = response.data[key];
    const keyMap = mappings[index];
    let resultData: keyType | keyType[];
    if (typeData instanceof Array) {
      resultData = typeData.map((entry: Record<string, JSONPrimitive>) =>
        convert<T, keyType>(entry, keyMap, key)
      );
    } else {
      resultData = convert<T, keyType>(typeData, keyMap, key);
    }
    return [key, resultData];
  });
  return Object.fromEntries(convertedData);
}

/** Calls to specific API endpoints **/

interface UserResponse extends APIResponse {
  group: Group;
  user: User;
}
const USER_MAP = new Map<string, keyof User>([
  ["auth0_user_id", "auth0UserId"],
  ["group_admin", "groupAdmin"],
  ["system_admin", "systemAdmin"],
]);
export const fetchUserData = (): Promise<UserResponse> =>
  apiResponse<UserResponse>(
    ["group", "user"],
    [null, USER_MAP],
    "/api/usergroup"
  );

interface SampleResponse extends APIResponse {
  samples: Sample[];
}
const SAMPLE_MAP = new Map<string, keyof Sample>([
  ["collection_date", "collectionDate"],
  ["collection_location", "collectionLocation"],
  ["private_identifier", "privateId"],
  ["public_identifier", "publicId"],
  ["upload_date", "uploadDate"],
]);
export const fetchSamples = (): Promise<SampleResponse> =>
  apiResponse<SampleResponse>(["samples"], [SAMPLE_MAP], "/api/samples");

interface TreeResponse extends APIResponse {
  phylo_trees: Tree[];
}
const TREE_MAP = new Map<string, keyof Tree>([
  ["phylo_tree_id", "id"],
  ["pathogen_genome_count", "pathogenGenomeCount"],
  ["completed_date", "creationDate"],
]);
export const fetchTrees = (): Promise<TreeResponse> =>
  apiResponse<TreeResponse>(["phylo_trees"], [TREE_MAP], "/api/phylo_trees");
