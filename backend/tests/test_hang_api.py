def test_rail_list_carries_cap_and_active_count(client):
    rails = client.get("/api/rails").json()
    a = next(r for r in rails if r["label"] == "A 杆")
    b = next(r for r in rails if r["label"] == "B 杆")
    assert a["max_items"] == 2
    assert a["active_count"] == 2
    assert b["max_items"] is None
    assert b["active_count"] == 1


def test_hang_skips_rail_at_item_cap(client):
    # A 杆上限 2、已挂 2 件；HR-2003 长 50cm 而 A 剩余 120cm，仍必须跳过 A、落到 B
    res = client.post("/api/hang", json={"order_id": 3})
    assert res.status_code == 200
    occ_a = client.get("/api/occupancy/1").json()
    occ_b = client.get("/api/occupancy/2").json()
    assert occ_a["active_count"] == 2
    assert {s["ticket_code"] for s in occ_a["segments"]} == {"HR-2001", "HR-2002"}
    assert occ_b["active_count"] == 2
    assert any(s["ticket_code"] == "HR-2003" for s in occ_b["segments"])


def test_hang_rejects_when_pinned_to_full_rail(client):
    # 指定达上限的 A 杆且无其他候选 -> 拒绝
    res = client.post("/api/hang", json={"order_id": 3, "rail_id": 1})
    assert res.status_code == 409
    occ_a = client.get("/api/occupancy/1").json()
    assert occ_a["active_count"] == 2


def test_pickup_lowers_count_then_hang_allowed(client):
    # 取走 A 杆一件，在挂件数降为 1，新件可再上 A
    assert client.post("/api/pickup", json={"ticket_code": "HR-2001"}).status_code == 200
    res = client.post("/api/hang", json={"order_id": 4})  # HR-2004 连衣裙 30cm
    assert res.status_code == 200
    occ_a = client.get("/api/occupancy/1").json()
    assert occ_a["active_count"] == 2
    tickets = {s["ticket_code"] for s in occ_a["segments"]}
    assert "HR-2004" in tickets
    assert "HR-2001" not in tickets


def test_cap_below_active_count_is_rejected(client):
    res = client.put("/api/rails/1", json={"max_items": 1})
    assert res.status_code == 400
    # 不低于当前件数的上限可以保存
    ok = client.put("/api/rails/1", json={"max_items": 3})
    assert ok.status_code == 200
    assert ok.json()["max_items"] == 3
    # 显式置空 = 取消件数限制
    cleared = client.put("/api/rails/1", json={"max_items": None})
    assert cleared.status_code == 200
    assert cleared.json()["max_items"] is None


def test_cap_must_be_positive(client):
    assert client.put("/api/rails/2", json={"max_items": 0}).status_code == 422
