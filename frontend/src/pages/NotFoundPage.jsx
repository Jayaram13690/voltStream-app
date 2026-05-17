import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-vs-bg text-vs-text">
      <h1 className="text-6xl font-bold text-vs-primary mb-4">404</h1>
      <h2 className="text-2xl font-semibold mb-4">Page Not Found</h2>
      <p className="text-lg mb-8 max-w-md text-center">
        The page you're looking for doesn't exist or has been moved.
      </p>
      <Link
        to="/"
        className="px-6 py-3 bg-vs-primary text-white rounded-lg hover:bg-vs-primary-dark transition-colors"
      >
        Go to Dashboard
      </Link>
    </div>
  );
}