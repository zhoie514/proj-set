# coding:utf-8
# ana_query_csv脚本生成的文件搞成zip并发送
# 发送给其他用户

"""将生成的所有csv 压缩 并邮件发送"""
import logging
import os
import zipfile
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

import CONF

logging.basicConfig(format='%(asctime)s|%(levelname)s|ana_email%(message)s', level=logging.INFO,
                    filename='log_email.txt')


def makezip(src_dir: str, gen_dir: str, force=False, date="2020-01-01"):
    """搬运，压缩文件夹,force：true为强制压缩覆盖，false的话，如果有文件就不重新压缩了
    :para src_dir  需要压缩的目录
    :para gen_dir  压缩文件的目标目录
    """
    zip_name = gen_dir + "/" + src_dir.split("/")[-1] + f"-format-{date}" + ".zip"
    F_NAME = zip_name.split('/')[-1]

    if not os.path.isdir(gen_dir):
        os.mkdir(gen_dir)

    if os.path.isfile(zip_name) and force is False:
        # 已有文件就不重复压缩了
        return F_NAME
    z = zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED)
    for dirpath, dirnames, filenames in os.walk(src_dir):
        fpath = src_dir.replace(src_dir, "")
        fpath = fpath and fpath + os.sep or ""
        for zip_name in filenames:
            z.write(os.path.join(dirpath, zip_name), fpath + zip_name)
    logging.info("zip succ")
    return F_NAME


SENDER = CONF.MAIL_USER


def sendmail(toAddr: list, att_name: str, date: str, att2: str = ""):
    # 带附件的email 实例
    MESSAGE = MIMEMultipart()

    # 绑定一个正文
    if not att2:
        MESSAGE.attach(MIMEText("上农的各位老师好：\r\n    这是今天的助贷流量的统计，请查收！\r\n    谢谢！", 'plain', "utf8"))
    else:
        MESSAGE.attach(MIMEText("说明：Excel版本的统计表是基于CSV内容统计的数据 \r\n [内部数据]", 'plain', "utf8"))

    # 定义一个附件
    att1 = MIMEText(open(f'{CONF.ZIP_EXCEL}/{att_name}', 'rb').read(), 'base64', 'utf-8')
    att1['Content-Type'] = 'application/octet-stream'
    # 设置附件1的名字
    att1['Content-Disposition'] = f'attachment; filename="{att_name}"'
    # 绑定此附件
    MESSAGE.attach(att1)
    # 设置发件人
    MESSAGE['From'] = Header(CONF.MAIL_USER, "utf-8")
    # 设置收件人
    MESSAGE['To'] = Header(";".join(toAddr), 'utf-8')
    # 邮件的大标题
    SUBJECT = f'{date}-Excel 表格统计'
    MESSAGE['Subject'] = Header(SUBJECT, "utf-8")
    if att2:
        # 添加额外的附件
        att2_name = att2.split('/')[-1]
        extra_att = MIMEText(open(att2, 'rb').read(), 'base64', 'utf-8')
        extra_att['Content-Type'] = 'application/octet-stream'
        extra_att['Content-Disposition'] = f'attachment;filename="{att2_name}"'
        MESSAGE.attach(extra_att)
    try:
        smtpobj = smtplib.SMTP_SSL()
        smtpobj.connect(CONF.MAIL_HOST, 465)
        smtpobj.login(CONF.MAIL_USER, CONF.MAIL_PWD)
        smtpobj.sendmail(SENDER, toAddr, MESSAGE.as_string())
        logging.info("send email succ")
    except smtplib.SMTPException as e:
        err = f'failed: {e}'
        logging.error(err)


if __name__ == '__main__':
    # 转换一下日期,为昨天
    # date = (datetime.now() + timedelta(days=CONF.DATE_OFFSET)).strftime("%Y%m%d")
    date = (datetime.now() + timedelta(days=-1)).strftime("%Y%m%d")

    zip_file_name = makezip(f"{CONF.ZIP_EXCEL_SOURCE}", CONF.ZIP_EXCEL, force=True, date=date)
    att2 = f"csv/gen_zips/{date}_qry_res.zip"

    # 内部发邮件函数
    sendmail(CONF.EMAIL_LIST, zip_file_name, date, att2=att2)
    # 对外发邮件函数
    sendmail(CONF.EMAIL_LIST_SRCB, zip_file_name, date)
