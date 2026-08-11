import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import App from "./App";
import "@testing-library/jest-dom";

describe("App component", () => {
  it("renders the dashboard page by default", () => {
    render(<App />);
    const heading = screen.getByText("Clinical Dashboard");
    expect(heading).toBeInTheDocument();
  });
});
