import { useEffect, useState } from "react";
import { api } from "../api/client";
type Rail = { id: number; label: string; length_cm: number };
type Occ = { rail_id: number; label: string; length_cm: number; max_items: number | null; active_count: number; segments: { ticket_code: string; garment_name: string; start_cm: number; end_cm: number }[] };
export default function OccupancyPage() {
  const [rails, setRails] = useState<Rail[]>([]);
  const [maps, setMaps] = useState<Occ[]>([]);
  useEffect(() => {
    api<Rail[]>("/rails").then(async rs => {
      setRails(rs);
      const all = await Promise.all(rs.map(r => api<Occ>(`/occupancy/${r.id}`)));
      setMaps(all);
    });
  }, []);
  return (<>
    <h2>占位图（横向尺线）</h2>
    {maps.map(m => (
      <div className="ruler-wrap" key={m.rail_id}>
        <div className="ruler-label">
          <span>{m.label}<span className={m.max_items != null && m.active_count >= m.max_items ? " cap-full" : " cap-count"}>
            {" "}· {m.active_count} 件{m.max_items != null ? ` / 上限 ${m.max_items}` : " / 件数不限"}
            {m.max_items != null && m.active_count >= m.max_items && "（已满）"}
          </span></span>
          <span className="mono">0 — {m.length_cm} cm</span>
        </div>
        <div className="ruler">
          {m.segments.map((s, i) => (
            <div key={i} className="seg" style={{ left: `${(s.start_cm / m.length_cm) * 100}%`, width: `${((s.end_cm - s.start_cm) / m.length_cm) * 100}%` }}
              title={`${s.ticket_code} ${s.start_cm}-${s.end_cm}cm`}>
              {s.garment_name}
            </div>
          ))}
        </div>
      </div>
    ))}
    {!rails.length && <p>暂无挂杆</p>}
  </>);
}
