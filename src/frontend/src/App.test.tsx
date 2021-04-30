import { render, screen } from "@testing-library/react";
import React from "react";
import App from "./App";

test("renders the App", () => {
  render(<App />);
  const linkElement = screen.getByText(/Loading.../i);
  expect(linkElement).toBeInTheDocument();
});
