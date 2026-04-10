export default function EmptyState({title,subtitle,action}) {
  return <div className="p-8 text-center opacity-80"><h3 className="text-lg font-semibold">{title}</h3><p className="mt-1">{subtitle}</p>{action}</div>;
}
