export function stripProtocol(url?: string): string {
  if (!url) {
    return "";
  }
  const re = /^[^:]*:\/\//i;
  return url.replace(re, "");
}
