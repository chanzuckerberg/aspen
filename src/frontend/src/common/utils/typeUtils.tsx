// credit: Typescript documentation, src
// https://www.typescriptlang.org/docs/handbook/advanced-types.html#index-types
// gets a property from an object.
export function get<T, K extends keyof T>(o: T, propertyName: K): T[K] {
  return o[propertyName]; // o[propertyName] is of type T[K]
}

// Take in a whole or subset of an API response that corresponds
// to a defined type in the frontend, along with a mapping of
// differing keys (e.g. if we're going from snake_case to camelCase)
// and converts the data to an object of that type with the right keys.
// Any keys not explicitly set in the mapping will be transferred to the
// new object.
export function jsonToType<T>(
  inputObject: Record<string, JSONPrimitive>,
  keyMap: Map<string, string | number> | null
): T {
  const entries: Array<Array<JSONPrimitive>> = [];
  Object.keys(inputObject).forEach((key) => {
    if (keyMap === null) {
      entries.push([key, inputObject[key]]);
    } else if (keyMap.has(key)) {
      entries.push([keyMap.get(key) as string, inputObject[key]]);
    } else {
      entries.push([key, inputObject[key]]);
    }
  });
  return Object.fromEntries(entries);
}

export function stringGuard(value: any): string {
  if (typeof value !== "string") {
    return String(value);
  }
  return value;
}
