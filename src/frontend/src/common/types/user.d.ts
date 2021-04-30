interface Group {
  [index: string]: JSONPrimitive;
  type: "Group";
  address: string;
  email: string;
  id: number;
  name: string;
}

interface User {
  [index: string]: JSONPrimitive;
  type: "User";
  auth0UserId: string;
  email: string;
  groupAdmin: boolean;
  groupId: number;
  id: number;
  name: string;
  systemAdmin: boolean;
  agreedToTos: boolean;
}
