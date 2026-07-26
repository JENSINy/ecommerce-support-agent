function ErrorBanner({ message }) {
  if (!message) {
    return null;
  }

  return <div className="global-error">{message}</div>;
}

export default ErrorBanner;
