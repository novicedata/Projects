DROP DATABASE robo;

create database robo
  default character set utf8mb4
  default collate utf8mb4_general_ci;

use robo;

########### 유형별 테이블 생성 ############
create table if not exists asset_master (
  asset_id        varchar(32) primary key,
  asset_name      varchar(100) not null,
  asset_class     varchar(20) not null,      -- CASH, KR_EQ, GLB_EQ, GOLD, LT_BOND
  source          varchar(20) not null,      -- STOOQ
  ticker          varchar(32) not null,      -- bil.us, ewy.us ...
  currency        varchar(10) not null default 'USD',
  is_active       tinyint(1) not null default 1
) engine=InnoDB default charset=utf8mb4;

create table if not exists raw_price_daily (
  asset_id    varchar(32) not null,
  dt          date not null,
  open        decimal(18,6) null,
  high        decimal(18,6) null,
  low         decimal(18,6) null,
  close       decimal(18,6) null,
  volume      decimal(24,2) null,
  source      varchar(20) not null,
  ingested_at timestamp not null default current_timestamp,
  primary key (asset_id, dt),
  constraint fk_raw_asset foreign key (asset_id) references asset_master(asset_id)
) engine=InnoDB default charset=utf8mb4;

create table if not exists feat_asset_monthly (
  asset_id   varchar(32) not null,
  eom        date not null,
  px_eom     decimal(18,6) not null,
  ret_1m     decimal(18,10) null,
  ret_3m     decimal(18,10) null,
  ret_12m    decimal(18,10) null,
  vol_3m     decimal(18,10) null,
  dd_6m      decimal(18,10) null,
  dd_12m     decimal(18,10) null,
  primary key (asset_id, eom),
  constraint fk_feat_asset foreign key (asset_id) references asset_master(asset_id)
) engine=InnoDB default charset=utf8mb4;
########################################

################ 자산 등록 ###############
insert into asset_master (asset_id, asset_name, asset_class, source, ticker, currency, is_active)
values
('CASH_BIL',     'Cash Proxy (BIL)',              'CASH',   'STOOQ', 'bil.us', 'USD', 1),
('KR_EQ_EWY',    'Korea Equity Proxy (EWY)',      'KR_EQ',  'STOOQ', 'ewy.us', 'USD', 1),
('GLB_EQ_VTI',   'US Equity Proxy (VTI)',         'GLB_EQ', 'STOOQ', 'vti.us', 'USD', 1),
('GOLD_GLD',     'Gold Proxy (GLD)',              'GOLD',   'STOOQ', 'gld.us', 'USD', 1),
('LT_BOND_TLT',  'Long-Term Bond Proxy (TLT)',    'LT_BOND','STOOQ', 'tlt.us', 'USD', 1)
on duplicate key update
  asset_name=values(asset_name),
  asset_class=values(asset_class),
  source=values(source),
  ticker=values(ticker),
  currency=values(currency),
  is_active=values(is_active);
########################################

#############시장 국면 테이블###############
create table regime_monthly (
  eom date not null,
  regime_code varchar(20) not null,
  regime_name varchar(50) not null,
  rule_json json null,
  vti_ret_3m double null,
  vti_vol_3m double null,
  vti_dd_6m  double null,
  created_at timestamp not null default current_timestamp,
  primary key (eom)
) engine=InnoDB default charset=utf8mb4;
########################################

##############포트폴리오 결과###############
create table portfolio_monthly (
  eom date not null,
  profile varchar(20) not null,        -- CONSERVATIVE / AGGRESSIVE
  policy varchar(20) not null,         -- CAP_RP / PRED_MVO / MDD_GUARD
  asset_id varchar(50) not null,
  weight DECIMAL(10,6) NOT NULL,
  meta_json json null,                 -- 제약/근거/파라미터(LLM 입력용)
  created_at timestamp not null default current_timestamp,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  primary key (eom, profile, policy, asset_id),
  index idx_port_eom (eom),
  index idx_port_prof (profile),
  constraint fk_port_asset foreign key (asset_id) references asset_master(asset_id)
) engine=InnoDB default charset=utf8mb4;
########################################

############## PRED_MVO용 ##############
create table mu_pred_monthly (
  eom date not null,                   -- “이 시점에서” 다음달을 예측
  asset_id varchar(32) not null,
  mu_1m double null,                   -- 예측된 다음달 기대수익
  model_name varchar(30) not null,
  meta_json json null,
  created_at timestamp not null default current_timestamp,
  primary key (eom, asset_id, model_name),
  constraint fk_mu_asset foreign key (asset_id) references asset_master(asset_id)
) engine=InnoDB default charset=utf8mb4;
########################################

##############정책 선택 로그###############
create table policy_choice_monthly (
  eom date not null,
  profile varchar(20) not null,
  regime_code varchar(20) not null,
  policy varchar(20) not null,
  created_at timestamp not null default current_timestamp,
  primary key (eom, profile)
) engine=InnoDB default charset=utf8mb4;
########################################

################XAI 결과#################
CREATE TABLE IF NOT EXISTS xai_policy_monthly (
  eom DATE NOT NULL,
  profile VARCHAR(20) NOT NULL,
  policy  VARCHAR(20) NOT NULL,
  target  VARCHAR(30) NOT NULL,     -- equity_total or asset_id
  top_features_json JSON NOT NULL,  -- [{"feature": "...", "value": ..., "shap": ...}, ...]
  base_value DOUBLE NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (eom, profile, policy, target)
);
########################################

commit;

select asset_id, asset_name, ticker, asset_class
from asset_master
where is_active=1
order by asset_id;


commit;

select * from asset_master;
select * from feat_asset_monthly;
select * from raw_price_daily;
select * from regime_monthly;
select * from portfolio_monthly;