from app.data import EQUIPMENT


def list_equipment():
    return list(EQUIPMENT.values())


def check_availability(equipment_id: int, quantity: int, department: str | None = None):
    equipment = EQUIPMENT.get(equipment_id)
    if equipment is None:
        return None
    available = equipment["available_quantity"]
    if department == "general":
        # 일반 부서는 지급 후 최소 1대가 남아야 한다.
        can_allocate = quantity <= available - 1
    else:
        # IT 부서와 부서 생략(기존 호출)은 남은 수량까지 지급 가능하다.
        can_allocate = quantity <= available
    return {
        "equipment_id": equipment_id,
        "requested_quantity": quantity,
        "available_quantity": available,
        "can_allocate": can_allocate,
    }
