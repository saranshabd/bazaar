export function Shimmer({
  className = "",
}: {
  className?: string;
}) {
  return <div className={`shimmer rounded-md ${className}`} />;
}