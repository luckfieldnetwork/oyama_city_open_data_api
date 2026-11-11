# -*- coding: utf-8 -*-
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Request
from sqlmodel import Session
from database import get_session
from crud import get_records
from schemas import dataset_models

router = APIRouter(tags=["データセット (Datasets)"])

@router.get(
    "/aed_locations",
    response_model=List[dataset_models.AedLocationsItem],
    summary="AED設置場所",
    description="AED設置場所（テーブル: aed_locations）のレコード一覧を取得します。",
)
def get_aed_locations(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "aed_locations", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/agricultural_sewage_facilities",
    response_model=List[dataset_models.AgriculturalSewageFacilitiesItem],
    summary="農業集落排水処理施設",
    description="農業集落排水処理施設（テーブル: agricultural_sewage_facilities）のレコード一覧を取得します。",
)
def get_agricultural_sewage_facilities(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "agricultural_sewage_facilities", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/bicycle_parking_lots",
    response_model=List[dataset_models.BicycleParkingLotsItem],
    summary="公共駐輪場一覧",
    description="公共駐輪場一覧（テーブル: bicycle_parking_lots）のレコード一覧を取得します。",
)
def get_bicycle_parking_lots(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "bicycle_parking_lots", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/calendar_events",
    response_model=List[dataset_models.CalendarEventsItem],
    summary="投票所一覧",
    description="投票所一覧（テーブル: calendar_events）のレコード一覧を取得します。",
)
def get_calendar_events(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "calendar_events", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/childcare_facilities",
    response_model=List[dataset_models.ChildcareFacilitiesItem],
    summary="子育て施設一覧",
    description="子育て施設一覧（テーブル: childcare_facilities）のレコード一覧を取得します。",
)
def get_childcare_facilities(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "childcare_facilities", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/community_care_recipients",
    response_model=List[dataset_models.CommunityCareRecipientsItem],
    summary="要介護認定者数",
    description="要介護認定者数（テーブル: community_care_recipients）のレコード一覧を取得します。",
)
def get_community_care_recipients(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "community_care_recipients", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/cultural_properties",
    response_model=List[dataset_models.CulturalPropertiesItem],
    summary="文化財一覧",
    description="文化財一覧（テーブル: cultural_properties）のレコード一覧を取得します。",
)
def get_cultural_properties(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "cultural_properties", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/drainage_pump_stations",
    response_model=List[dataset_models.DrainagePumpStationsItem],
    summary="排水機場",
    description="排水機場（テーブル: drainage_pump_stations）のレコード一覧を取得します。",
)
def get_drainage_pump_stations(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "drainage_pump_stations", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/evacuation_sites",
    response_model=List[dataset_models.EvacuationSitesItem],
    summary="避難所一覧",
    description="避難所一覧（テーブル: evacuation_sites）のレコード一覧を取得します。",
)
def get_evacuation_sites(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "evacuation_sites", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/facility_care_recipients",
    response_model=List[dataset_models.FacilityCareRecipientsItem],
    summary="介護相談先（高齢者サポートセンター）",
    description="介護相談先（高齢者サポートセンター）（テーブル: facility_care_recipients）のレコード一覧を取得します。",
)
def get_facility_care_recipients(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "facility_care_recipients", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/farmland_rent_rates",
    response_model=List[dataset_models.FarmlandRentRatesItem],
    summary="農地賃借料情報",
    description="農地賃借料情報（テーブル: farmland_rent_rates）のレコード一覧を取得します。",
)
def get_farmland_rent_rates(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "farmland_rent_rates", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/farmland_stats",
    response_model=List[dataset_models.FarmlandStatsItem],
    summary="大規模小売店舗一覧",
    description="大規模小売店舗一覧（テーブル: farmland_stats）のレコード一覧を取得します。",
)
def get_farmland_stats(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "farmland_stats", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/fire_dept_coop_businesses",
    response_model=List[dataset_models.FireDeptCoopBusinessesItem],
    summary="小山市消防団協力事業所",
    description="小山市消防団協力事業所（テーブル: fire_dept_coop_businesses）のレコード一覧を取得します。",
)
def get_fire_dept_coop_businesses(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "fire_dept_coop_businesses", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/fire_dept_support_businesses",
    response_model=List[dataset_models.FireDeptSupportBusinessesItem],
    summary="消防団サポート事業所",
    description="消防団サポート事業所（テーブル: fire_dept_support_businesses）のレコード一覧を取得します。",
)
def get_fire_dept_support_businesses(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "fire_dept_support_businesses", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/fire_hydrants",
    response_model=List[dataset_models.FireHydrantsItem],
    summary="消防水利施設一覧",
    description="消防水利施設一覧（テーブル: fire_hydrants）のレコード一覧を取得します。",
)
def get_fire_hydrants(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "fire_hydrants", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/fire_rescue_ambulance_stats",
    response_model=List[dataset_models.FireRescueAmbulanceStatsItem],
    summary="火災救助救急件数",
    description="火災救助救急件数（テーブル: fire_rescue_ambulance_stats）のレコード一覧を取得します。",
)
def get_fire_rescue_ambulance_stats(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "fire_rescue_ambulance_stats", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/fire_trucks",
    response_model=List[dataset_models.FireTrucksItem],
    summary="消防団車両一覧",
    description="消防団車両一覧（テーブル: fire_trucks）のレコード一覧を取得します。",
)
def get_fire_trucks(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "fire_trucks", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/first_aid_stations",
    response_model=List[dataset_models.FirstAidStationsItem],
    summary="救急ステーション認定事業所一覧",
    description="救急ステーション認定事業所一覧（テーブル: first_aid_stations）のレコード一覧を取得します。",
)
def get_first_aid_stations(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "first_aid_stations", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/home_care_recipients",
    response_model=List[dataset_models.HomeCareRecipientsItem],
    summary="地区別要介護認定者数",
    description="地区別要介護認定者数（テーブル: home_care_recipients）のレコード一覧を取得します。",
)
def get_home_care_recipients(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "home_care_recipients", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/insured_category1",
    response_model=List[dataset_models.InsuredCategory1Item],
    summary="第1号被保険者数",
    description="第1号被保険者数（テーブル: insured_category1）のレコード一覧を取得します。",
)
def get_insured_category1(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "insured_category1", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/manufacturing_mining_stats",
    response_model=List[dataset_models.ManufacturingMiningStatsItem],
    summary="イベント情報",
    description="イベント情報（テーブル: manufacturing_mining_stats）のレコード一覧を取得します。",
)
def get_manufacturing_mining_stats(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "manufacturing_mining_stats", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/medical_institutions",
    response_model=List[dataset_models.MedicalInstitutionsItem],
    summary="医療機関一覧",
    description="医療機関一覧（テーブル: medical_institutions）のレコード一覧を取得します。",
)
def get_medical_institutions(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "medical_institutions", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/medical_institutions_v2",
    response_model=List[dataset_models.MedicalInstitutionsV2Item],
    summary="医療機関一覧",
    description="医療機関一覧（テーブル: medical_institutions_v2）のレコード一覧を取得します。",
)
def get_medical_institutions_v2(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "medical_institutions_v2", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/nursery_schools",
    response_model=List[dataset_models.NurserySchoolsItem],
    summary="市内工業系組織",
    description="市内工業系組織（テーブル: nursery_schools）のレコード一覧を取得します。",
)
def get_nursery_schools(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "nursery_schools", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/nursing_care_benefits",
    response_model=List[dataset_models.NursingCareBenefitsItem],
    summary="介護事業者一覧",
    description="介護事業者一覧（テーブル: nursing_care_benefits）のレコード一覧を取得します。",
)
def get_nursing_care_benefits(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "nursing_care_benefits", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/nursing_care_certified",
    response_model=List[dataset_models.NursingCareCertifiedItem],
    summary="保険給付費状況",
    description="保険給付費状況（テーブル: nursing_care_certified）のレコード一覧を取得します。",
)
def get_nursing_care_certified(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "nursing_care_certified", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/nursing_care_providers",
    response_model=List[dataset_models.NursingCareProvidersItem],
    summary="小中義務教育学校通学区域情報",
    description="小中義務教育学校通学区域情報（テーブル: nursing_care_providers）のレコード一覧を取得します。",
)
def get_nursing_care_providers(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "nursing_care_providers", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/park_facilities",
    response_model=List[dataset_models.ParkFacilitiesItem],
    summary="公園施設一覧",
    description="公園施設一覧（テーブル: park_facilities）のレコード一覧を取得します。",
)
def get_park_facilities(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "park_facilities", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/police_fire_facilities",
    response_model=List[dataset_models.PoliceFireFacilitiesItem],
    summary="警察施設一覧",
    description="警察施設一覧（テーブル: police_fire_facilities）のレコード一覧を取得します。",
)
def get_police_fire_facilities(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "police_fire_facilities", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/population_by_age",
    response_model=List[dataset_models.PopulationByAgeItem],
    summary="大字町丁名別世帯数人口統計",
    description="大字町丁名別世帯数人口統計（テーブル: population_by_age）のレコード一覧を取得します。",
)
def get_population_by_age(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "population_by_age", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/population_by_district",
    response_model=List[dataset_models.PopulationByDistrictItem],
    summary="年齢別人口統計",
    description="年齢別人口統計（テーブル: population_by_district）のレコード一覧を取得します。",
)
def get_population_by_district(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "population_by_district", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/public_housing",
    response_model=List[dataset_models.PublicHousingItem],
    summary="公営住宅一覧",
    description="公営住宅一覧（テーブル: public_housing）のレコード一覧を取得します。",
)
def get_public_housing(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "public_housing", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/public_toilets",
    response_model=List[dataset_models.PublicToiletsItem],
    summary="公衆トイレ一覧",
    description="公衆トイレ一覧（テーブル: public_toilets）のレコード一覧を取得します。",
)
def get_public_toilets(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "public_toilets", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/public_wifi",
    response_model=List[dataset_models.PublicWifiItem],
    summary="公衆無線LANアクセスポイント一覧",
    description="公衆無線LANアクセスポイント一覧（テーブル: public_wifi）のレコード一覧を取得します。",
)
def get_public_wifi(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "public_wifi", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/sightseeing_info",
    response_model=List[dataset_models.SightseeingInfoItem],
    summary="観光情報",
    description="観光情報（テーブル: sightseeing_info）のレコード一覧を取得します。",
)
def get_sightseeing_info(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "sightseeing_info", filters=filters, q=q, limit=limit, offset=offset)

@router.get(
    "/tourist_facilities",
    response_model=List[dataset_models.TouristFacilitiesItem],
    summary="公共施設一覧",
    description="公共施設一覧（テーブル: tourist_facilities）のレコード一覧を取得します。",
)
def get_tourist_facilities(
    request: Request,
    session: Session = Depends(get_session),
    q: Optional[str] = Query(None, description="キーワード検索 (全カラム対象の部分一致)"),
    limit: int = Query(50, ge=1, le=1000, description="取得件数上限 (最大1000件)"),
    offset: int = Query(0, ge=0, description="取得開始位置 (オフセット)"),
):
    filters = {k: v for k, v in request.query_params.items() if k not in ("limit", "offset", "q")}
    return get_records(session, "tourist_facilities", filters=filters, q=q, limit=limit, offset=offset)
