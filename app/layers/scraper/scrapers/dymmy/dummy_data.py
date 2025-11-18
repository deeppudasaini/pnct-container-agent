# core/scraper/dummy.py

DUMMY_CONTAINERS = [
    {
        "container_number": "MSDU4234521",
        "available": "Yes",
        "location": "Yard 21",
        "trucker": "ABC Trucking",
        "customs_status": "Released",
        "freight_status": "Paid",
        "misc_holds": "None",
        "terminal_demurrage_amount": "$0",
        "last_free_day": "2024-11-20",
        "last_guarantee_day": "2024-11-22",
        "pay_through_date": "2024-11-25",
        "non_demurrage_amount": "$0",
        "ssco": "MAEU",
        "type": "DRY",
        "length": "40",
        "height": "9.6",
        "hazardous": "No",
        "genset_required": "No",
    },
    {
        "container_number": "MSMU8317127",
        "available": "No",
        "location": "Ship Bay 2",
        "trucker": "XYZ Logistics",
        "customs_status": "On Hold",
        "freight_status": "Pending",
        "misc_holds": "HOLD",
        "terminal_demurrage_amount": "$120",
        "last_free_day": "2024-11-18",
        "last_guarantee_day": "2024-11-19",
        "pay_through_date": "2024-11-20",
        "non_demurrage_amount": "$55",
        "ssco": "HLCU",
        "type": "REEFER",
        "length": "20",
        "height": "8.6",
        "hazardous": "No",
        "genset_required": "Yes",
    },
    {
        "container_number": "MSBU5011443",
        "available": "No",
        "location": "Ship Bay 6",
        "trucker": "Some Logistics",
        "customs_status": "On Hold",
        "freight_status": "Pending",
        "misc_holds": "HOLD",
        "terminal_demurrage_amount": "130",
        "last_free_day": "2024-11-18",
        "last_guarantee_day": "2024-11-19",
        "pay_through_date": "2024-11-20",
        "non_demurrage_amount": "$55",
        "ssco": "HLCU",
        "type": "REEFER",
        "length": "20",
        "height": "8.6",
        "hazardous": "No",
        "genset_required": "Yes",
    }
]
# core/scraper/dummy.py

def build_dummy_html(container_number: str) -> str:
    container = next(
        (c for c in DUMMY_CONTAINERS if c["container_number"] == container_number),
        None
    )

    # If container not found → empty table body
    if container is None:
        row_html = ""
    else:
        c = container
        row_html = f"""
        <tr>
            <td>{c['container_number']}</td>
            <td>{c['available']}</td>
            <td>{c['location']}</td>
            <td>{c['trucker']}</td>
            <td>{c['customs_status']}</td>
            <td>{c['freight_status']}</td>
            <td>{c['misc_holds']}</td>
            <td>{c['terminal_demurrage_amount']}</td>
            <td>{c['last_free_day']}</td>
            <td>{c['last_guarantee_day']}</td>
            <td>{c['pay_through_date']}</td>
            <td>{c['non_demurrage_amount']}</td>
            <td>{c['ssco']}</td>
            <td>{c['type']}</td>
            <td>{c['length']}</td>
            <td>{c['height']}</td>
            <td>{c['hazardous']}</td>
            <td>{c['genset_required']}</td>
        </tr>
        """

    return f"""
<!DOCTYPE html>
<html>
<head>
    <title>Container Availability Results</title>
</head>
<body>
    <div class="mt-4 mb-4 table-responsive scrollbar-deep-purple bordered-deep-purple thin square">
        <table class="table table-sm z-depth-1 table-hover">
            <thead class="cloudy-knoxville-gradient">
                <tr>
                    <th>Container Number</th>
                    <th>Available</th>
                    <th>Location</th>
                    <th>Trucker</th>
                    <th>Customs Status</th>
                    <th>Freight Status</th>
                    <th>Misc Holds</th>
                    <th>Terminal Demurrage Amount</th>
                    <th>Last Free Day</th>
                    <th>Last Guar. Day</th>
                    <th>Pay Through Date</th>
                    <th>Non Demurrage Amount</th>
                    <th>SSCO</th>
                    <th>Type</th>
                    <th>Length</th>
                    <th>Height</th>
                    <th>Hazardous</th>
                    <th>Genset Required</th>
                </tr>
            </thead>
            <tbody>
                {row_html}
            </tbody>
        </table>
    </div>
</body>
</html>
"""
