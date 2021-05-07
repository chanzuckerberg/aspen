export const GISAID_STATUS_TO_TEXT: Record<
  Sample["gisaid"]["status"],
  string
> = {
  accepted: "Accepted",
  no_info: "Not Yet Submitted",
  not_eligible: "Not Eligible",
  rejected: "Rejected",
  submitted: "Submitted",
};
