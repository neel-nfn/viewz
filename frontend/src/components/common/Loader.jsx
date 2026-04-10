export default function Loader({label='Loading...'}) {
  return <div role="status" className="flex items-center gap-2 p-4"><span className="loading loading-spinner" />{label}</div>;
}
