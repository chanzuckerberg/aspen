// refactor as needed
import axios from "axios";
import { jsonToType } from "src/common/utils";

export enum API {
  USER_DATA = "/api/usergroup",
  SAMPLES = "/api/samples",
  LOG_IN = "/login",
  LOG_OUT = "/logout",
  PHYLO_TREES = "/api/phylo_trees",
}

export const DEFAULT_FETCH_OPTIONS: RequestInit = {
  credentials: "include",
};

export const DEFAULT_PUT_OPTIONS: RequestInit = {
  credentials: "include",
  method: "PUT",
};

export const DEFAULT_HEADERS_MUTATION_OPTIONS: RequestInit = {
  headers: {
    "Content-Type": "application/json",
  },
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
  ["group_id", "groupdId"],
  ["agreed_to_tos", "agreedToTos"],
]);
export const fetchUserData = (): Promise<UserResponse> =>
  apiResponse<UserResponse>(["group", "user"], [null, USER_MAP], API.USER_DATA);

export const updateUserData = (user: Partial<User>): Promise<Response> => {
  return fetch(process.env.API_URL + API.USER_DATA, {
    ...DEFAULT_PUT_OPTIONS,
    ...DEFAULT_HEADERS_MUTATION_OPTIONS,
    body: JSON.stringify(user),
  });
};

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
  apiResponse<SampleResponse>(["samples"], [SAMPLE_MAP], API.SAMPLES);

interface TreeResponse extends APIResponse {
  phylo_trees: Tree[];
}
const TREE_MAP = new Map<string, keyof Tree>([
  ["phylo_tree_id", "id"],
  ["pathogen_genome_count", "pathogenGenomeCount"],
  ["completed_date", "creationDate"],
]);
export const fetchTrees = (): Promise<TreeResponse> =>
  apiResponse<TreeResponse>(["phylo_trees"], [TREE_MAP], API.PHYLO_TREES);

export const logout = (): Promise<Response> => {
  return fetch(process.env.API_URL + API.LOG_OUT, DEFAULT_FETCH_OPTIONS);
};
