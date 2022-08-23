SELECT
	pas.EPISODE_NUMBER ,
	count (pas.EPISODE_NUMBER),
	pas.admission_date ,
	pas.date_of_birth ,
	pas.race_value ,
	pas.sex_value ,
	pas.sexual_orientation_value ,
	pas.gender_identity_value ,
	pas.veteran_status_value ,
	pas.military_status_value ,
	CASE
		WHEN pas.pru_no = '06594' THEN 'Bellport OP'
		WHEN pas.pru_no = '06635' THEN 'Bellport Day'
		WHEN pas.pru_no = '07210' THEN 'Richmond Hill'
		WHEN pas.pru_no = '51847' THEN 'Greenpoint'
		WHEN pas.pru_no = '52648' THEN 'Brentwood'
		WHEN pas.pru_no = '53002' THEN 'OH2'
		WHEN pas.pru_no = '53003' THEN 'OH1'
		WHEN pas.pru_no = '53263' THEN 'Brentwood Womens'
		WHEN pas.pru_no = '53093' THEN 'ORC'
		WHEN pas.pru_no = '53483' THEN 'React'
		WHEN pas.pru_no = '53558' THEN 'ORC Mens'
		WHEN pas.pru_no = '8272001A' THEN 'OMH'
		ELSE pas.pru_no
	END AS pru_no,
	pas.type_of_residence_value ,
	pas.living_arrangements_value ,
	pas.highest_grade_compl_value ,
	pas.employment_status_value ,
	pas.marital_status_value ,
	pas.veteran_status_value ,
	pas.experienced_trauma_value ,
	pas.mental_illness_value ,
	pas.prim_substance_type_value ,
	pas.prim_substance_route_value ,
	pas.prim_substance_freq_value ,
	pas.prim_substance_age ,
	pas.sec_substance_type_value ,
	pas.sec_substance_route_value ,
	pas.sec_substance_freq_value ,
	pas.sec_substance_age ,
	pas.tert_substance_type_value ,
	pas.tert_substance_route_value ,
	pas.tert_substance_freq_value ,
	pas.tert_substance_age ,
	(
	SELECT
		TOP 1
		cifi.sliding_fee_income
	FROM
		System.call_intake_financial_inv as cifi
	WHERE
		cifi.PATID = pas.PATID
	ORDER BY 
		cifi.fin_invest_eff_date desc) as household_income , 
	(
	SELECT
		TOP 1 pa.age_first_intoxication
	FROM
		CWSSYSTEM.Psychosocial_Assessment as pa
	WHERE
		pa.PATID = pas.PATID
	ORDER BY
		pa.Data_Entry_Date desc) as first_intoxication ,
	(
	SELECT
		TOP 1 pa.sor_overdose_Value
	FROM
		CWSSYSTEM.Psychosocial_Assessment as pa
	WHERE
		pa.PATID = pas.PATID
	ORDER BY
		pa.Data_Entry_Date desc) as sor_overdose , 
	(
	SELECT
		TOP 1 pa.si_best_friend_Value
	FROM
		CWSSYSTEM.Psychosocial_Assessment as pa
	WHERE
		pa.PATID = pas.PATID
	ORDER BY
		pa.Data_Entry_Date desc) as best_friend , 
	(
	SELECT
		TOP 1 pasec.mh_suic_homic_act_Value
	FROM
		CWSSYSTEM.Psychosocial_Assessment_Sec as pasec
	WHERE
		pasec.PATID = pas.PATID
	ORDER BY
		pasec.Data_Entry_Date desc) as suicide_act , 
	(
	SELECT
		TOP 1 pasec.mh_suic_homic_idea_Value
	FROM
		CWSSYSTEM.Psychosocial_Assessment_Sec as pasec
	WHERE
		pasec.PATID = pas.PATID
	ORDER BY
		pasec.Data_Entry_Date desc) as suicide_idea ,  
	(
	SELECT
		TOP 1 pasec.scr_score_tot
	FROM
		CWSSYSTEM.Psychosocial_Assessment_Sec as pasec
	WHERE
		pasec.PATID = pas.PATID
	ORDER BY
		pasec.Data_Entry_Date desc) as mh_score ,
	(
	SELECT
		'yes'
	FROM
		CWSInfoScrb.Rx AS rx
	WHERE
		pas.PATID = rx.PATID) AS Medicated ,
	(
	SELECT
		'yes'
	from
		CWSInfoScrb.Rx as rx
	WHERE
		rx.PATID = pas.PATID
		and rx.drugname in ('NALTREXONE', 'Naltrexone', 'NALTREXONE HCL', 'Naltrexone HCl'
		, 'Buprenorphine Hydrochloride', 'BUPRENORPHINE-NALOXONE', 'Buprenorphine-Naloxone'
		, 'Suboxone', 'SUBOXONE (BUPRENORPHINE-NALOXONE)')
		) as MAT ,
	(
	SELECT
		'yes'
	FROM
		INCIDENT.incident_data_all AS ida
	JOIN INCIDENT.incident_client_involve ici ON
		ici.INCID = ida.INCID
	WHERE
		ici.PATID = pas.PATID
		AND ida.type_of_inc_value_short in ('ZONSITE SIGNIFICANT-OVERDOSE-ILLICIT DRUGS', 'OFFSITE-OVERDOSE', 'OFFSITE-OVERDOSE DEATH', 'ONSITE INCIDENT-MEDICAL EMERGENCY&ZONSITE SIGNIFICANT-OVERDOSE-PRESCRIPTION DRUGS')
	) as Overdose
FROM
	STATEFORM.nys_pas44_admit AS pas
WHERE 
        pas.admission_date > '2022-01-01'
ORDER BY
	admission_date DESC
