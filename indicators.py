from enum import Enum


class Indicators(Enum):
    """
    An enum containing all the sustainability indicators that are currently bein used, as well as indicators
    that have been commented out that are specifically for the LkSG law, as well as for the Sustainable
    Development Goals (SDGs).
    """
    SURFACE_WATER_POLLUTION = "Surface Water Pollution"
    BIODIVERSITY = "Biodiversity"
    # NOT_RELEVANT_TO_ESG = "Not Relevant to ESG"
    WASTEWATER_MANAGEMENT = "Wastewater Management"
    HAZARDOUS_MATERIALS_MANAGEMENT = "Hazardous Materials Management"
    DISCLOSURE = "Disclosure"
    SOIL_AND_GROUNDWATER_IMPACT = "Soil and Groundwater Impact"
    ANIMAL_WELFARE = "Animal Welfare"
    COMMUNITIES_HEALTH_AND_SAFETY = "Communities Health and Safety"
    CORPORATE_GOVERNANCE = "Corporate Governance"
    RESPONSIBLE_INVESTMENT_AND_GREENWASHING = "Responsible Investment & Greenwashing"
    SUPPLY_CHAIN_ECONOMIC_GOVERNANCE = "Supply Chain (Economic / Governance)"
    STRATEGY_IMPLEMENTATION = "Strategy Implementation"
    CLIMATE_RISKS = "Climate Risks"
    DISCRIMINATION = "Discrimination"
    EMPLOYEE_HEALTH_AND_SAFETY = "Employee Health and Safety"
    RISK_MANAGEMENT_AND_INTERNAL_CONTROL = "Risk Management and Internal Control"
    LEGAL_PROCEEDINGS_AND_LAW_VIOLATIONS = "Legal Proceedings & Law Violations"
    EMERGENCIES_ENVIRONMENTAL = "Emergencies (Environmental)"
    ENVIRONMENTAL_MANAGEMENT = "Environmental Management"
    LAND_REHABILITATION = "Land Rehabilitation"
    FREEDOM_OF_ASSOCIATION_AND_RIGHT_TO_ORGANISE = "Freedom of Association and Right to Organise"
    AIR_POLLUTION = "Air Pollution"
    CULTURAL_HERITAGE = "Cultural Heritage"
    FORCED_LABOUR = "Forced Labour"
    LABOR_RELATIONS_MANAGEMENT = "Labor Relations Management"
    WATER_CONSUMPTION = "Water Consumption"
    GREENHOUSE_GAS_EMISSIONS = "Greenhouse Gas Emissions"
    SUPPLY_CHAIN_ENVIRONMENTAL = "Supply Chain (Environmental)"
    PRODUCT_SAFETY_AND_QUALITY = "Product Safety and Quality"
    EMERGENCIES_SOCIAL = "Emergencies (Social)"
    NATURAL_RESOURCES = "Natural Resources"
    HUMAN_RIGHTS = "Human Rights"
    PHYSICAL_IMPACTS = "Physical Impacts"
    LAND_ACQUISITION_AND_RESETTLEMENT_E = "Land Acquisition and Resettlement (E)"
    WASTE_MANAGEMENT = "Waste Management"
    INDIGENOUS_PEOPLE = "Indigenous People"
    RETRENCHMENT = "Retrenchment"
    SUPPLY_CHAIN_SOCIAL = "Supply Chain (Social)"
    LAND_ACQUISITION_AND_RESETTLEMENT_S = "Land Acquisition and Resettlement (S)"
    MINIMUM_AGE_AND_CHILD_LABOUR = "Minimum Age and Child Labour"
    ENERGY_EFFICIENCY_AND_RENEWABLES = "Energy Efficiency and Renewables"
    LANDSCAPE_TRANSFORMATION = "Landscape Transformation"
    DATA_SAFETY = "Data Safety"
    ECONOMIC_CRIME = "Economic Crime"
    PLANNING_LIMITATIONS = "Planning Limitations"
    VALUES_AND_ETHICS = "Values and Ethics"

    """
    # LkSG indicators (translated to English). The comments behind each indicator are the relevant 
    # indicators of the above Enum mapped onto the LkSG indicators.

    M1 = "Child labor"  # Minimum Age and Child Labor
    M2 = "Forced labor and slavery"  # Forced Labor
    M3 = "Disregard for occupational health and safety and work-related health hazards"  # Employee Health and Safety
    M4 = "Disregard for freedom of association and the right to collective bargaining"  # Freedom of Association and 
                                                                                          Right to Organise
    M5 = "Unequal treatment in employment"  # Discrimination
    M6 = "Withholding of a fair wage"
    M7 = "Destruction of natural resources through environmental pollution"  # Land Rehabilitation, 
                                                                               Environmental Management, 
                                                                               Natural Resources
    M8 = "Unlawful violation of land rights" # Land Acquisition and Resettlement (E), 
                                               Land Acquisition and Resettlement (S)
    M9 = "Hiring or using security forces that may cause harm due to lack of instruction or control" # Communities 
                                                                                                       Health and Safety
    M10 = "Human rights violations"  # Human Rights
    U1 = "Prohibited production, use and/or disposal of mercury" # Hazardous Materials Management
    U2 = "Prohibited production, use, or non-environmentally sound handling of hazardous substances" # Hazardous 
                                                                                                       Materials 
                                                                                                       Management
    U3 = "Prohibited transboundary movements of hazardous wastes and their disposal" # Hazardous Materials Management
    """

    """
    # SDGs by the United Nations
    
    NO_POVERTY = "No poverty"
    ZERO_HUNGER = "Zero hunger"
    GOOD_HEALTH = "Good health and well-being"
    QUALITY_EDUCATION = "Quality education"
    GENDER_EQUALITY = "Gender equality"
    CLEAN_WATER = "Clean water and sanitation"
    CLEAN_ENERGY = "Affordable and clean energy"
    ECONOMIC_GROWTH = "Decent work and economic growth"
    INFRASTRUCTURE = "Industry, innovation and infrastructure"
    REDUCED_INEQUALITY = "Reduced inequality"
    SUSTAINABLE_CITIES = "Sustainable cities and communities"
    RESPONSIBLE_CONSUMPTION = "Responsible consumption and production"
    CLIMATE_ACTION = "Climate action"
    LIFE_BELOW_WATER = "Life below water"
    LIFE_ON_LAND = "Life on land"
    STRONG_INSTITUTIONS = "Peace, justice and strong institutions"
    # PARTNERSHIP = "Partnership for the goals"
    """
