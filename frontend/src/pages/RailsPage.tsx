import { useEffect, useState } from "react";
import { api } from "../api/client";
type R = { id: number; store_id: number; label: string; length_cm: number; max_items: number | null; active_count: number };
export default function RailsPage() {
  const [rows, setRows] = useState<R[]>([]);
  const [drafts, setDrafts] = useState<Record<number, string>>({});
  const [errs, setErrs] = useState<Record<number, string>>({});
  const [msg, setMsg] = useState("");
  const reload = () => api<R[]>("/rails").then(rs => {
    setRows(rs);
    setDrafts(Object.fromEntries(rs.map(r => [r.id, r.max_items == null ? "" : String(r.max_items)])));
  });
  useEffect(() => { reload(); }, []);
  async function save(r: R) {
    setMsg("");
    const raw = (drafts[r.id] ?? "").trim();
    const cap = raw === "" ? null : Number(raw);
    const next = { ...errs };
    if (cap !== null && (!Number.isInteger(cap) || cap < 1)) {
      next[r.id] = "上限须为不小于 1 的整数";
    } else if (cap !== null && cap < r.active_count) {
      next[r.id] = `不能小于当前在挂件数 ${r.active_count}`;
    }
    if (next[r.id]) { setErrs(next); return; }
    try {
      await api<R>(`/rails/${r.id}`, { method: "PUT", body: JSON.stringify({ max_items: cap }) });
      delete next[r.id]; setErrs(next);
      setMsg(`${r.label} 件数上限已保存`);
      reload();
    } catch (e) {
      let text = e instanceof Error ? e.message : String(e);
      try { text = JSON.parse(text).detail ?? text; } catch { /* 非 JSON 错误体，原样展示 */ }
      setErrs({ ...next, [r.id]: text });
    }
  }
  return (<>
    <h2>挂杆</h2>
    {msg && <div className="ok">{msg}</div>}
    <table className="table"><thead><tr><th>标签</th><th>门店</th><th>长度 cm</th><th>在挂件数</th><th>件数上限</th><th></th></tr></thead>
    <tbody>{rows.map(r => {
      const atCap = r.max_items != null && r.active_count >= r.max_items;
      return (<tr key={r.id}>
        <td>{r.label}</td>
        <td>{r.store_id}</td>
        <td className="mono">{r.length_cm}</td>
        <td className={atCap ? "err mono" : "mono"}>{r.active_count}{r.max_items != null ? ` / ${r.max_items}` : " / 不限"}{atCap && "（已满）"}</td>
        <td>
          <input value={drafts[r.id] ?? ""} onChange={e => setDrafts({ ...drafts, [r.id]: e.target.value })}
            placeholder="不限" inputMode="numeric" style={{ width: 90 }} />
          {errs[r.id] && <div className="err" style={{ fontSize: ".78rem" }}>{errs[r.id]}</div>}
        </td>
        <td><button onClick={() => save(r)}>保存上限</button></td>
      </tr>);
    })}</tbody></table>
  </>);
}
