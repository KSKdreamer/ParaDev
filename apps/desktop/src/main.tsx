import { createRoot } from "react-dom/client";
import App from "./App";
import { RendererErrorBoundary } from "./components/RendererErrorBoundary";
import "./styles/theme.css";
import "./styles/app.css";

const root = document.getElementById("root");

if (!root) {
  throw new Error("ParaDev desktop root element was not found.");
}

createRoot(root).render(
  <RendererErrorBoundary>
    <App />
  </RendererErrorBoundary>
);
