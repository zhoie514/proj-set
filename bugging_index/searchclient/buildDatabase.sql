DROP table  if exists errorlist;
drop table if exists qanda;
drop table if exists ocrmap;
drop table if exists err_index;
drop table if exists qanda_index;

create table errorlist(
  id integer  primary key autoincrement,
  e_orign  text,
  e_describe text,
  e_interface text,
  e_mask text,
  e_category text,
  e_errorinfo text,
  e_logsearch text,
  e_procedure text
);
--
create table qanda(
  id integer primary key autoincrement,
  q_orign text,
  q_ques text,
  q_ans text
);
--
create table ocrmap(
  id integer  primary key autoincrement,
  o_type text,
  o_code text,
  o_msg text
);
--
create  table err_index(
  id integer primary key autoincrement,
  r_content text,
  r_id text
);
--
create table qanda_index(
  id integer primary key autoincrement ,
  r_content text,
  r_id text
);
--
