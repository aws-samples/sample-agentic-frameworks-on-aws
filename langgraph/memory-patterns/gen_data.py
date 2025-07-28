from agentic_memory.base import BaseCheckPointer,BaseEpisodicStore, BaseLongTermStore
from agentic_memory.implementation import CheckPointerInMemory, EpisodicStoreFile, LongTermStoreFile
from agentic_memory.orchestrator import MultiTierMemoryOrchestrator
from datetime import datetime, timezone

def generate_episodic_data():
    episodic = EpisodicStoreFile()
    key = ("cust_789", "1HGBH41JXMN109186")
    
    episodic.put(key, {
        "service_type": "Engine Diagnostic",
        "mileage": 28000,
        "dealer": "Precision Auto",
        "technician_checks": [
            "Scanned ECU for error codes",
            "Performed compression test on all cylinders",
            "Inspected spark plug condition and gap",
            "Checked fuel pressure and injector pulse"
        ],
        "issues_observed": [
            "Error code P0302: Cylinder 2 misfire detected",
            "Compression low in cylinder 2",
            "Spark plug in cylinder 2 fouled with carbon deposits"
        ],
        "customer_agreement": "Customer agreed to recommended repairs after explanation of findings and estimated costs.",
        "service_notes": "Customer was shown diagnostic results and agreed to replace spark plugs and perform further testing if issue persists.",
        "service_date": datetime.now(timezone.utc).isoformat()
    })
    
    episodic.put(key, {
        "service_type": "Spark Plug & Coil Replacement",
        "mileage": 28010,
        "dealer": "Precision Auto",
        "technician_checks": [
            "Removed all spark plugs for inspection",
            "Tested ignition coil resistance and output",
            "Checked wiring harness for continuity"
        ],
        "issues_observed": [
            "Spark plug in cylinder 2 heavily fouled",
            "Ignition coil for cylinder 2 intermittently failing"
        ],
        "customer_agreement": "Customer approved replacement of all spark plugs and faulty ignition coil.",
        "service_notes": "Replaced all spark plugs with OEM parts, replaced cylinder 2 coil, cleared codes, and performed test drive.",
        "service_date": datetime.now(timezone.utc).isoformat()
    })
    
    episodic.put(key, {
        "service_type": "Coolant Leak Inspection",
        "mileage": 28500,
        "dealer": "Cooling Experts",
        "technician_checks": [
            "Pressure tested cooling system",
            "Inspected radiator, hoses, and water pump",
            "Checked coolant reservoir for cracks"
        ],
        "issues_observed": [
            "Slow coolant leak detected at lower radiator hose clamp",
            "Coolant level below minimum mark"
        ],
        "customer_agreement": "Customer approved hose clamp replacement and coolant top-up.",
        "service_notes": "Replaced faulty clamp, topped off coolant, and advised customer to monitor level.",
        "service_date": datetime.now(timezone.utc).isoformat()
    })
    
    episodic.put(key, {
        "service_type": "Brake System Overhaul",
        "mileage": 29000,
        "dealer": "Brake Masters",
        "technician_checks": [
            "Measured brake pad and rotor thickness",
            "Checked brake fluid for contamination",
            "Inspected calipers and brake lines for leaks"
        ],
        "issues_observed": [
            "Front pads worn to 2mm, rotors scored",
            "Brake fluid dark and slightly contaminated"
        ],
        "customer_agreement": "Customer agreed to replace front pads, rotors, and flush brake fluid after being shown worn components.",
        "service_notes": "Replaced front pads and rotors, flushed brake fluid, test drove to confirm braking performance.",
        "service_date": datetime.now(timezone.utc).isoformat()
    })
    
    episodic.put(key, {
        "service_type": "Battery & Charging System Check",
        "mileage": 29500,
        "dealer": "Battery World",
        "technician_checks": [
            "Tested battery voltage and CCA",
            "Checked alternator output under load",
            "Inspected battery terminals and cables"
        ],
        "issues_observed": [
            "Battery failed load test",
            "Alternator output normal",
            "Corrosion on positive terminal"
        ],
        "customer_agreement": "Customer approved battery replacement and terminal cleaning.",
        "service_notes": "Installed new battery, cleaned terminals, verified charging system operation.",
        "service_date": datetime.now(timezone.utc).isoformat()
    })
    
    episodic.put(key, {
        "service_type": "Air Conditioning Service",
        "mileage": 30000,
        "dealer": "Climate Comfort",
        "technician_checks": [
            "Checked refrigerant pressure",
            "Inspected compressor clutch operation",
            "Tested cabin air temperature"
        ],
        "issues_observed": [
            "Low refrigerant pressure",
            "Compressor clutch engaging intermittently"
        ],
        "customer_agreement": "Customer agreed to A/C recharge and compressor clutch replacement.",
        "service_notes": "Recharged system, replaced clutch, confirmed cold air output at all settings.",
        "service_date": datetime.now(timezone.utc).isoformat()
    })
    
    episodic.put(key, {
        "service_type": "Transmission Service",
        "mileage": 30500,
        "dealer": "TransFix",
        "technician_checks": [
            "Checked transmission fluid level and color",
            "Scanned for transmission-related error codes",
            "Test drove vehicle for shifting performance"
        ],
        "issues_observed": [
            "Fluid dark and slightly burnt odor",
            "No error codes, but slight hesitation on upshift"
        ],
        "customer_agreement": "Customer agreed to fluid change and filter replacement.",
        "service_notes": "Replaced fluid and filter, shifting improved, advised customer to return if hesitation persists.",
        "service_date": datetime.now(timezone.utc).isoformat()
    })
    
    episodic.put(key, {
        "service_type": "Suspension Noise Diagnosis",
        "mileage": 31000,
        "dealer": "RideRight Suspension",
        "technician_checks": [
            "Inspected struts, shocks, and bushings",
            "Test drove vehicle over bumps",
            "Checked sway bar links"
        ],
        "issues_observed": [
            "Front left sway bar link loose",
            "Minor wear in strut bushings"
        ],
        "customer_agreement": "Customer approved replacement of sway bar link and deferred strut bushing replacement.",
        "service_notes": "Replaced sway bar link, noise eliminated, advised monitoring of bushings.",
        "service_date": datetime.now(timezone.utc).isoformat()
    })
    
    episodic.put(key, {
        "service_type": "Exhaust Leak Repair",
        "mileage": 31500,
        "dealer": "Exhaust Pros",
        "technician_checks": [
            "Inspected exhaust manifold and gaskets",
            "Checked for leaks using smoke test",
            "Listened for noise during cold start"
        ],
        "issues_observed": [
            "Small leak at exhaust manifold gasket",
            "Audible ticking noise on cold start"
        ],
        "customer_agreement": "Customer agreed to gasket replacement after being shown leak location.",
        "service_notes": "Replaced manifold gasket, verified no leaks, noise resolved.",
        "service_date": datetime.now(timezone.utc).isoformat()
    })
    
    episodic.put(key, {
        "service_type": "Detailed Multi-Point Inspection",
        "mileage": 32000,
        "dealer": "AllCare Auto",
        "technician_checks": [
            "Checked all fluid levels and conditions",
            "Inspected belts, hoses, and filters",
            "Tested lights, wipers, and horn",
            "Examined tire tread and brakes"
        ],
        "issues_observed": [
            "Serpentine belt showing minor cracks",
            "Cabin air filter dirty",
            "Left rear tire tread nearing wear bar"
        ],
        "customer_agreement": "Customer agreed to replace belt and filter, declined tire replacement at this time.",
        "service_notes": "Replaced serpentine belt and cabin filter, noted tire for next visit.",
        "service_date": datetime.now(timezone.utc).isoformat()
    })
    
    episodic.put(('cust_011', '1HGCM82633A004352'), {
        'service_type': 'Brake Inspection and Repair',
        'mileage': 36200,
        'dealer': 'Metro Brake Center',
        'technician_checks': [
            'Removed all wheels to inspect brake pads and rotors',
            'Measured pad thickness and rotor wear with calipers',
            'Checked brake fluid level and condition',
            'Inspected brake lines for leaks or corrosion'
        ],
        'issues_observed': [
            'Front brake pads worn to 1.5mm, rotors scored',
            'Rear pads at 3mm, still serviceable',
            'Brake fluid slightly dark, no leaks found'
        ],
        'customer_agreement': 'Customer agreed to front pad and rotor replacement, and requested brake fluid flush after seeing worn parts.',
        'service_notes': 'Replaced front pads and rotors with OEM parts, flushed brake fluid, performed road test to confirm smooth braking and no noise.',
        'service_date': datetime.now(timezone.utc).isoformat()
    })
    
    episodic.put(('cust_012', '2T1BURHE6JC074321'), {
        'service_type': 'Electrical System Diagnosis',
        'mileage': 41800,
        'dealer': 'City Auto Electric',
        'technician_checks': [
            'Scanned for diagnostic trouble codes (DTCs)',
            'Tested battery, alternator, and starter output',
            'Checked fuses and relays for continuity',
            'Inspected wiring harness for signs of wear or rodent damage'
        ],
        'issues_observed': [
            'Battery voltage low, alternator charging at 13.9V (normal)',
            'Found intermittent short in trunk light circuit',
            'Customer reported dashboard flicker when using power windows'
        ],
        'customer_agreement': 'Customer approved battery replacement and trunk circuit repair after being shown test results.',
        'service_notes': 'Replaced battery, repaired wiring, verified all electrical systems functioned normally after repair.',
        'service_date': datetime.now(timezone.utc).isoformat()
    })
    
    episodic.put(('cust_013', 'WBA3A5C53DF123456'), {
        'service_type': 'Oil Leak and Engine Noise Investigation',
        'mileage': 76500,
        'dealer': 'German Auto Specialists',
        'technician_checks': [
            'Inspected engine bay for oil residue and leaks',
            'Checked valve cover, oil pan, and timing cover gaskets',
            'Listened for ticking noise at cold start and idle',
            'Monitored oil pressure with mechanical gauge'
        ],
        'issues_observed': [
            'Oil seepage at valve cover gasket',
            'Ticking noise from top end, likely hydraulic lifters',
            'Oil level slightly low, pressure within spec'
        ],
        'customer_agreement': 'Customer agreed to replace valve cover gasket and flush engine oil after being shown leak location.',
        'service_notes': 'Replaced gasket, flushed oil, added lifter additive, noise reduced. Customer advised to monitor and return if noise persists.',
        'service_date': datetime.now(timezone.utc).isoformat()
    })
    
    episodic.put(('cust_014', '1FTFW1EF1EKF51234'), {
        'service_type': 'Suspension and Steering Evaluation',
        'mileage': 90200,
        'dealer': 'TruckPro Service',
        'technician_checks': [
            'Lifted vehicle and inspected front and rear suspension components',
            'Checked ball joints, bushings, and tie rods for play',
            'Test drove vehicle to reproduce customer’s reported clunk',
            'Measured alignment angles'
        ],
        'issues_observed': [
            'Front lower ball joints loose with excessive play',
            'Rear leaf spring bushings cracked',
            'Steering wheel slightly off-center'
        ],
        'customer_agreement': 'Customer approved replacement of ball joints and bushings, and requested alignment service.',
        'service_notes': 'Replaced ball joints and bushings, performed 4-wheel alignment, verified clunk eliminated on test drive.',
        'service_date': datetime.now(timezone.utc).isoformat()
    })
    
    episodic.put(('cust_015', '3FA6P0HR6ER123789'), {
        'service_type': 'A/C System Repair',
        'mileage': 50400,
        'dealer': 'CoolAir Automotive',
        'technician_checks': [
            'Checked refrigerant pressure and system charge',
            'Inspected compressor clutch operation and relay',
            'Checked cabin air filter and blower motor function',
            'Used UV dye to check for leaks'
        ],
        'issues_observed': [
            'Low refrigerant charge, small leak at condenser fitting',
            'Compressor clutch engaging intermittently',
            'Cabin filter moderately dirty'
        ],
        'customer_agreement': 'Customer agreed to condenser repair, recharge, and filter replacement after being shown leak evidence.',
        'service_notes': 'Repaired condenser fitting, replaced filter, recharged system, verified cold air output and no further leaks.',
        'service_date': datetime.now(timezone.utc).isoformat()
    })
    
    episodic.put(('cust_016', '5NPE24AF6FH123456'), {
        'service_type': 'Steering Vibration Diagnosis',
        'mileage': 62000,
        'dealer': 'Precision Tire & Alignment',
        'technician_checks': [
            'Balanced all four wheels and checked for bent rims',
            'Inspected tie rods and control arms for wear',
            'Checked tire tread and inflation',
            'Test drove at highway speeds'
        ],
        'issues_observed': [
            'Two wheels out of balance, one rim slightly bent',
            'Minor play in right outer tie rod end',
            'Front tires worn unevenly'
        ],
        'customer_agreement': 'Customer approved wheel balancing and tie rod replacement. Deferred rim repair for future visit.',
        'service_notes': 'Balanced wheels, replaced tie rod, rotated tires, steering vibration reduced. Advised customer on rim repair options.',
        'service_date': datetime.now(timezone.utc).isoformat()
    })
    
    episodic.put(('cust_017', 'JHMGE8H59DC123456'), {
        'service_type': 'Rear Brake Service',
        'mileage': 81500,
        'dealer': 'Urban Brake Shop',
        'technician_checks': [
            'Inspected rear pads, rotors, and calipers',
            'Checked parking brake adjustment',
            'Measured rotor thickness and checked for scoring',
            'Test drove to reproduce noise'
        ],
        'issues_observed': [
            'Rear pads at wear indicator, rotors glazed',
            'Parking brake slightly loose',
            'Squeal present during low-speed stops'
        ],
        'customer_agreement': 'Customer agreed to rear pad and rotor replacement, and parking brake adjustment.',
        'service_notes': 'Replaced pads and rotors, adjusted parking brake, confirmed no noise on test drive.',
        'service_date': datetime.now(timezone.utc).isoformat()
    })
    
    episodic.put(('cust_018', '1N4AL3AP7JC123456'), {
        'service_type': 'Engine Hesitation and Idle Repair',
        'mileage': 67300,
        'dealer': 'Nissan Service Center',
        'technician_checks': [
            'Scanned for error codes and live data',
            'Inspected mass airflow sensor and throttle body',
            'Checked vacuum hoses for leaks',
            'Test drove vehicle for hesitation and idle quality'
        ],
        'issues_observed': [
            'Error code P0101: MAF sensor out of range',
            'Throttle body carbon buildup',
            'Vacuum hose loose at intake'
        ],
        'customer_agreement': 'Customer approved MAF sensor replacement and throttle cleaning after being shown scan results.',
        'service_notes': 'Replaced MAF sensor, cleaned throttle body, secured vacuum hose, idle and acceleration normalized.',
        'service_date': datetime.now(timezone.utc).isoformat()
    })
    
    episodic.put(('cust_019', '4T1BF1FK7GU123456'), {
        'service_type': 'Battery Drain and Electrical Diagnosis',
        'mileage': 48900,
        'dealer': 'Toyota Certified Service',
        'technician_checks': [
            'Tested battery and alternator output',
            'Checked for parasitic draw with multimeter',
            'Inspected trunk light and glove box circuits',
            'Verified keyless entry function'
        ],
        'issues_observed': [
            'Parasitic draw of 0.25A traced to trunk light circuit',
            'Battery voltage drops below 12V overnight',
            'Keyless entry intermittent'
        ],
        'customer_agreement': 'Customer approved trunk circuit repair and battery replacement.',
        'service_notes': 'Repaired trunk wiring, installed new battery, confirmed normal draw and keyless entry operation.',
        'service_date': datetime.now(timezone.utc).isoformat()
    })
    
    episodic.put(('cust_020', '1C4RJFBG6FC123456'), {
        'service_type': '4WD System Fault Diagnosis',
        'mileage': 103200,
        'dealer': 'Jeep Specialist Garage',
        'technician_checks': [
            'Scanned for drivetrain and 4WD system codes',
            'Inspected transfer case and actuator wiring',
            'Checked fluid level and condition in transfer case',
            'Test drove vehicle to reproduce warning light'
        ],
        'issues_observed': [
            'Code C140F: Transfer case actuator fault',
            'Wiring harness corroded at connector',
            '4WD warning light triggered during test drive'
        ],
        'customer_agreement': 'Customer approved actuator and wiring repair after being shown code and corrosion.',
        'service_notes': 'Replaced actuator, repaired harness, cleared codes, confirmed 4WD operation and no warning light.',
        'service_date': datetime.now(timezone.utc).isoformat()
    })


def generate_long_term_data():
    long_term = LongTermStoreFile()
    
    long_term.put("1HGCM82633A004352", {
        "issue_summary": "Intermittent stalling during acceleration, especially in stop-and-go traffic. Customer noticed the issue was more frequent on humid days.",
        "resolution": "Cleaned and replaced the throttle body, recalibrated the ECU, and replaced faulty spark plugs. Test drive confirmed resolution.",
        "service_engineer": "Alice Johnson",
        "service_date": "2024-10-22",
        "additional_notes": "Customer reported significant improvement post-service; advised follow-up in 3 months."
    })
    
    long_term.put("2T1BURHE6JC074321", {
        "issue_summary": "Persistent check engine light with error code P0420 indicating catalyst system efficiency below threshold.",
        "resolution": "Replaced catalytic converter and upstream oxygen sensor. Cleared codes and verified emissions system operation.",
        "service_engineer": "Brian Lee",
        "service_date": "2025-02-13",
        "additional_notes": "Warranty covered replacement; customer advised on fuel quality."
    })
    
    long_term.put("WBA3A5C53DF123456", {
        "issue_summary": "Noticeable oil leak under the engine bay, with burning oil smell after long drives.",
        "resolution": "Replaced valve cover gasket and cleaned engine bay. Monitored for further leaks during test drive.",
        "service_engineer": "Carla Schmidt",
        "service_date": "2025-03-08",
        "additional_notes": "Recommended regular oil checks; no further leak observed after service."
    })
    
    long_term.put("1FTFW1EF1EKF51234", {
        "issue_summary": "Grinding noise from front suspension when turning at low speeds.",
        "resolution": "Replaced worn lower ball joints and lubricated suspension components. Noise eliminated after repair.",
        "service_engineer": "David Kim",
        "service_date": "2025-01-27",
        "additional_notes": "Suggested periodic suspension inspection due to vehicle usage."
    })
    
    long_term.put("3FA6P0HR6ER123789", {
        "issue_summary": "Air conditioning intermittently blows warm air, especially during idling.",
        "resolution": "Recharged A/C system, replaced faulty compressor clutch, and checked for leaks. System performance restored.",
        "service_engineer": "Elena Garcia",
        "service_date": "2024-09-15",
        "additional_notes": "No leaks found; advised customer to monitor A/C performance."
    })
    
    long_term.put("5NPE24AF6FH123456", {
        "issue_summary": "Steering wheel vibration at highway speeds, especially above 60 mph.",
        "resolution": "Balanced all four wheels, replaced two worn tires, and performed alignment. Test drive confirmed smooth operation.",
        "service_engineer": "Frank Martin",
        "service_date": "2025-04-10",
        "additional_notes": "Customer advised to rotate tires every 5,000 miles."
    })
    
    long_term.put("JHMGE8H59DC123456", {
        "issue_summary": "Rear brake squeal and reduced braking performance noticed after rainy weather.",
        "resolution": "Replaced rear brake pads and rotors, cleaned caliper hardware, and applied anti-squeal compound.",
        "service_engineer": "Grace Liu",
        "service_date": "2025-05-18",
        "additional_notes": "Customer advised to return if noise recurs."
    })
    
    long_term.put("1N4AL3AP7JC123456", {
        "issue_summary": "Engine hesitates during acceleration and rough idle, especially when cold.",
        "resolution": "Replaced mass airflow sensor and cleaned throttle body. Idle and acceleration normalized.",
        "service_engineer": "Hector Ramirez",
        "service_date": "2025-06-01",
        "additional_notes": "Recommended use of top-tier gasoline."
    })
    
    long_term.put("4T1BF1FK7GU123456", {
        "issue_summary": "Battery repeatedly discharges overnight, requiring jump starts.",
        "resolution": "Diagnosed parasitic drain from trunk light circuit; repaired wiring and replaced battery.",
        "service_engineer": "Irene Novak",
        "service_date": "2025-03-22",
        "additional_notes": "No further discharge after repair; customer satisfied."
    })
    
    long_term.put("1C4RJFBG6FC123456", {
        "issue_summary": "4WD warning light illuminated, with occasional loss of power to rear wheels.",
        "resolution": "Replaced transfer case control module and updated system firmware. 4WD system fully operational after service.",
        "service_engineer": "James Patel",
        "service_date": "2025-02-28",
        "additional_notes": "Customer advised to return for any future drivetrain alerts."
    })
    
    long_term.put("2G1FB1E34F9123456", {
        "issue_summary": "Persistent misfire on cylinder 3, check engine light illuminated, and noticeable loss of power during acceleration.",
        "resolution": "Performed compression test, found low compression in cylinder 3. Replaced faulty fuel injector and spark plug, and performed ECU relearn procedure.",
        "service_engineer": "Karen Thompson",
        "service_date": "2025-04-22",
        "additional_notes": "Customer advised to use premium fuel and return if symptoms recur."
    })
    
    long_term.put("JN1CV6AP3BM123456", {
        "issue_summary": "Navigation system freezes intermittently and audio system resets while driving.",
        "resolution": "Updated navigation firmware, replaced failing audio control module, and checked all related wiring harnesses.",
        "service_engineer": "Liam O'Sullivan",
        "service_date": "2025-05-10",
        "additional_notes": "No further issues observed after extensive road test."
    })
    
    long_term.put("WA1DGAFE7FD012345", {
        "issue_summary": "Excessive oil consumption between scheduled changes; customer required top-ups every 1,000 miles.",
        "resolution": "Replaced PCV valve, installed updated piston rings, and performed oil consumption test. Oil usage returned to normal range.",
        "service_engineer": "Marta Kowalski",
        "service_date": "2025-03-19",
        "additional_notes": "Recommended monitoring oil level monthly."
    })
    
    long_term.put("1FADP3F20EL123456", {
        "issue_summary": "Transmission shudder and delayed engagement when shifting from park to drive.",
        "resolution": "Updated transmission control module software, flushed transmission fluid, and replaced clutch packs.",
        "service_engineer": "Noah Williams",
        "service_date": "2025-01-30",
        "additional_notes": "Customer reported smoother shifting post-service."
    })
    
    long_term.put("3N1AB7AP0HY123456", {
        "issue_summary": "Unusual rattling noise from undercarriage at low speeds, especially when going over bumps.",
        "resolution": "Inspected exhaust system and found loose heat shield. Secured shield and replaced worn exhaust hanger.",
        "service_engineer": "Olivia Chen",
        "service_date": "2025-06-12",
        "additional_notes": "No noise detected after repair; customer satisfied."
    })
    
    long_term.put("5YJSA1E26GF123456", {
        "issue_summary": "Touchscreen display intermittently goes blank and resets, affecting climate control and navigation.",
        "resolution": "Replaced main display unit (MCU1) with upgraded MCU2, updated system software, and verified all functions.",
        "service_engineer": "Priya Singh",
        "service_date": "2025-03-05",
        "additional_notes": "Customer instructed on new features after upgrade."
    })
    
    long_term.put("1GNSKCKC0FR123456", {
        "issue_summary": "Rear air suspension fails to maintain ride height, causing uneven stance after parking overnight.",
        "resolution": "Replaced leaking rear air suspension bags and faulty compressor, recalibrated suspension system.",
        "service_engineer": "Robert Evans",
        "service_date": "2025-04-14",
        "additional_notes": "System held pressure after repair; follow-up scheduled in 1 month."
    })
    
    long_term.put("JH4KC1F57FC123456", {
        "issue_summary": "Adaptive cruise control disengages unexpectedly and warning light appears on dashboard.",
        "resolution": "Replaced radar sensor unit and performed ACC system calibration. Cleared all diagnostic codes.",
        "service_engineer": "Samantha Brooks",
        "service_date": "2025-02-25",
        "additional_notes": "Test drive confirmed normal adaptive cruise function."
    })
    
    long_term.put("1C6RR7MT1FS123456", {
        "issue_summary": "Intermittent 4WD engagement; vehicle sometimes stuck in 2WD despite selector position.",
        "resolution": "Replaced transfer case actuator motor and checked wiring harness for corrosion. 4WD system now operates as intended.",
        "service_engineer": "Victor Hernandez",
        "service_date": "2025-05-29",
        "additional_notes": "Advised customer to operate 4WD monthly to prevent actuator sticking."
    })
    
    long_term.put("SALWR2VF4FA123456", {
        "issue_summary": "Frequent coolant loss with no visible leaks; engine temperature warning on long drives.",
        "resolution": "Pressure tested cooling system, found internal leak in EGR cooler. Replaced EGR cooler and refilled coolant.",
        "service_engineer": "Wendy Zhang",
        "service_date": "2025-06-18",
        "additional_notes": "No further coolant loss after repair; customer advised to monitor coolant level."
    })

    long_term.put("1FA6P8TH0J5100001", {
        "issue_summary": "Customer reports intermittent engine misfire at idle and under acceleration, especially on cold mornings.",
        "resolution": "Replaced all spark plugs and ignition coils, cleaned fuel injectors, and updated engine control software. Misfire resolved.",
        "service_engineer": "Alex Morgan",
        "service_date": "2025-06-25",
        "additional_notes": "Recommended use of high-quality fuel and regular maintenance."
    })
    
    long_term.put("WDDZF4JB1JA123456", {
        "issue_summary": "Oil leak detected on garage floor and burning smell after highway driving.",
        "resolution": "Replaced valve cover gasket and oil pan seal, cleaned engine bay, and verified no further leaks during extended test drive.",
        "service_engineer": "Brigitte Keller",
        "service_date": "2025-05-30",
        "additional_notes": "Customer advised to monitor oil level and return for inspection in 2 months."
    })
    
    long_term.put("5YJ3E1EA7JF123456", {
        "make": "Tesla",
        "model": "Model 3",
        "year": 2018,
        "issue_summary": "Touchscreen display intermittently freezes, especially when using navigation and climate control simultaneously.",
        "resolution": "Performed system reboot, installed latest firmware update, and replaced main display unit under warranty.",
        "service_engineer": "Derek Lin",
        "service_date": "2025-06-10",
        "additional_notes": "Customer instructed on manual reset procedure if issue recurs."
    })
    
    long_term.put("1GNEV18K6JF123456", {
        "issue_summary": "Rear suspension sags after parking overnight and ride height is uneven.",
        "resolution": "Replaced rear air suspension bags and compressor, recalibrated height sensors, and verified operation.",
        "service_engineer": "Emily Carter",
        "service_date": "2025-06-05",
        "additional_notes": "Suggested regular suspension checks due to high mileage."
    })
    
    long_term.put("JHMCM56557C123456", {
        "issue_summary": "Battery drains overnight, requiring frequent jump starts. Parasitic draw suspected.",
        "resolution": "Diagnosed parasitic draw from glove box light circuit, repaired wiring, and replaced battery.",
        "service_engineer": "Franklin Stewart",
        "service_date": "2025-05-20",
        "additional_notes": "No further drain observed; customer advised to report any recurrence."
    })
    
    long_term.put("3FAHP0HA9AR123456", {
        "issue_summary": "Engine stalls unexpectedly at low speeds and during stop-and-go traffic.",
        "resolution": "Cleaned throttle body, replaced idle air control valve, and updated PCM software. Test drive confirmed issue resolved.",
        "service_engineer": "Gloria Martinez",
        "service_date": "2025-04-28",
        "additional_notes": "Customer advised to monitor idle quality and return if symptoms persist."
    })
    
    long_term.put("1HGCR2F3XEA123456", {
        "issue_summary": "Transmission shudders and hesitates when shifting from 2nd to 3rd gear.",
        "resolution": "Performed transmission fluid flush and replaced transmission control solenoid. Shifting improved significantly.",
        "service_engineer": "Henry Zhao",
        "service_date": "2025-06-15",
        "additional_notes": "Recommended transmission service every 30,000 miles."
    })
    
    long_term.put("1C4PJMCB1FW123456", {
        "issue_summary": "Coolant loss with no visible leaks; engine temperature warning light comes on during long drives.",
        "resolution": "Pressure tested cooling system, found leak at water pump gasket. Replaced water pump and gasket, refilled coolant.",
        "service_engineer": "Isabel Gomez",
        "service_date": "2025-06-01",
        "additional_notes": "Advised customer to monitor coolant level and schedule follow-up in 6 months."
    })
    
    long_term.put("1G1ZE5ST1GF123456", {
        "issue_summary": "A/C blows warm air at idle and low speeds, cools only while driving.",
        "resolution": "Replaced A/C compressor clutch and recharged system. Verified cold air output at all speeds.",
        "service_engineer": "Jasmine Patel",
        "service_date": "2025-05-18",
        "additional_notes": "No leaks detected; customer advised to run A/C regularly."
    })
    
    long_term.put("2T3ZF4DVXAW123456", {
        "issue_summary": "Rear brake squeal and reduced braking performance, especially after rainy days.",
        "resolution": "Replaced rear brake pads and rotors, lubricated caliper slides, and applied anti-squeal compound.",
        "service_engineer": "Kevin Nguyen",
        "service_date": "2025-06-11",
        "additional_notes": "Customer advised to return if noise recurs."
    })

    # Honda Accord - recurring stalling and idle issues
    long_term.put("1HGCM82633A004353", {
        "make": "Honda",
        "model": "Accord",
        "year": 2019,
        "issue_summary": "Engine stalls occasionally at red lights and during low-speed maneuvers. Idle speed fluctuates when the engine is warm.",
        "resolution": "Replaced idle air control valve, cleaned throttle body, and updated engine control software. Idle stabilized and no further stalling observed.",
        "service_engineer": "Alice Johnson",
        "service_date": "2025-07-01",
        "additional_notes": "Customer advised to return if stalling recurs."
    })
    
    long_term.put("1HGCM82633A004354", {
        "issue_summary": "Intermittent engine stalling at low speeds, especially after long periods of idling.",
        "resolution": "Inspected and replaced faulty crankshaft position sensor, cleaned fuel injectors. Monitored with scan tool; no further stalls.",
        "service_engineer": "Alice Johnson",
        "service_date": "2025-06-28",
        "additional_notes": "Recommended regular fuel system cleaning."
    })
    
    # Toyota Camry - battery drain and electrical issues
    long_term.put("4T1BF1FK7GU123457", {
        "issue_summary": "Battery discharges overnight, and keyless entry intermittently fails.",
        "resolution": "Identified parasitic draw from malfunctioning trunk latch sensor. Replaced sensor and battery, verified normal draw.",
        "service_engineer": "Irene Novak",
        "service_date": "2025-07-02",
        "additional_notes": "Customer advised to monitor for any further electrical issues."
    })
    
    long_term.put("4T1BF1FK7GU123458", {
        "issue_summary": "Recurring battery drain and dashboard warning lights after car is parked for two days.",
        "resolution": "Traced drain to aftermarket alarm system. Removed faulty system, replaced battery, and verified normal operation.",
        "service_engineer": "Irene Novak",
        "service_date": "2025-06-30",
        "additional_notes": "Recommended customer avoid aftermarket electronics."
    })
    
    # Ford Fusion - A/C and climate control issues
    long_term.put("3FA6P0HR6ER123790", {
        "issue_summary": "A/C system blows warm air intermittently, especially after extended use.",
        "resolution": "Replaced faulty A/C compressor relay and recharged refrigerant. System tested under various conditions; cold air restored.",
        "service_engineer": "Elena Garcia",
        "service_date": "2025-07-01",
        "additional_notes": "Customer advised to run A/C weekly to maintain system health."
    })
    
    long_term.put("3FA6P0HR6ER123791", {
        "issue_summary": "Climate control panel unresponsive and A/C only works at maximum setting.",
        "resolution": "Replaced climate control module and recalibrated system. Verified all settings functional.",
        "service_engineer": "Elena Garcia",
        "service_date": "2025-06-29",
        "additional_notes": "No further issues reported after follow-up call."
    })
    
    # Tesla Model 3 - touchscreen/display issues
    long_term.put("5YJ3E1EA7JF123457", {
        "issue_summary": "Touchscreen display randomly reboots while driving, causing temporary loss of navigation and media controls.",
        "resolution": "Installed latest firmware update and replaced touchscreen controller under warranty. Monitored for stability.",
        "service_engineer": "Derek Lin",
        "service_date": "2025-07-02",
        "additional_notes": "Customer instructed on reporting further software anomalies."
    })
    
    long_term.put("5YJ3E1EA7JF123458", {
        "issue_summary": "Intermittent freezing of main display, especially after rapid temperature changes.",
        "resolution": "Replaced main display unit (MCU), checked all connections, and performed system diagnostics. Issue resolved.",
        "service_engineer": "Derek Lin",
        "service_date": "2025-06-27",
        "additional_notes": "Customer advised to keep software updated."
    })

