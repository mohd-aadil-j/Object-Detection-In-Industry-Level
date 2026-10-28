# Frontend layer

The operator interface is a React application using JavaScript and JSX only.
TypeScript is intentionally not used. Vite provides local development and
production builds.

The initial operator dashboard provides settings configuration, start,
pause/resume, and stop controls, image upload, and clear pass, rework, and
inspection-error states. Vite proxies `/api` and `/media` to the local Django
server during development. It also provides refreshable history and CSV export.
