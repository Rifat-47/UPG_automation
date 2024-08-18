import random
import string

branch_codes = [
    # '0238',
    # '1336',
    # '0556',
    # '0252',
    # '0528',
    # '1488',
    # '0450',
    # '0208',
    # '0223',
    # '0379',
    # '0222',
    # '1493'
    '0010'
]

# stg random vo 1997
# train 46548
random_vo_no = 1997
total_vo = 1
member_in_vo = 5

def generate_random_name(length=5):
    letters = string.ascii_uppercase
    return ''.join(random.choice(letters) for _ in range(length))

queries = []

for branch_code in branch_codes:
    for i in range(total_vo):
        vo_name = generate_random_name()
        vo = f"""INSERT INTO erp_vo ("branch_code", "org_no", "vo_id", "vo_name", "collection_date", "branch_id", "created", "created_by", "group_name", "group_status_id", "is_active", "next_collection_date", "po_name", "po_pin", "updated", "updated_at", "updated_by")
            VALUES ('{branch_code}', '{random_vo_no}', '{random_vo_no}', '{vo_name}', '2024-05-05 00:00:00.000+0000', '333', NULL, NULL, 'UPG Group-02', '1', true, NULL, 'Shefali Begum', '189297', NULL, '2022-03-10 15:10:34', NULL);"""
        queries.append(vo)

        for j in range(member_in_vo):
            member = f"""INSERT INTO erp_vo_member ("branch_code", "vo_id", "org_no", "vo_name", "member_id", "member_name", "application_date", "branch_id", "created", "created_by", "group_name", "is_active", "member_enterprise", "member_status_id", "org_mem_no", "po_name", "po_pin", "updated", "updated_at", "updated_by")
                VALUES ('{branch_code}', '{random_vo_no}', '{random_vo_no}', '{vo_name}', '{random_vo_no}{random_vo_no}{j}', 'vo member {random_vo_no}{random_vo_no}{j}', '2022-04-06', '333', '2022-04-24 05:34:21.491+0000', NULL, 'UPG Group-03', true, NULL, 1, '2', NULL, '00163716', '2022-04-24 05:34:21.491+0000', '2022-04-07 08:43:03', NULL);"""
            queries.append(member)

        random_vo_no += 1


for query in queries:
    print(query)

print(len(queries))
