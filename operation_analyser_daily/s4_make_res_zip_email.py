# step3：将生成的CSV所在的文件夹压缩为日期_qry_res.zip的文件
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

logging.basicConfig(format='%(asctime)s|%(levelname)s|%(message)s', level=logging.INFO, filename='log_email.txt')


def makezip(src_dir: str, gen_dir: str, force=False):
    """搬运，压缩文件夹,force：true为强制压缩覆盖，false的话，如果有文件就不重新压缩了
    :para src_dir  需要压缩的目录
    :para gen_dir  压缩文件的目标目录
    """
    zip_name = gen_dir + "/" + src_dir.split("/")[-1] + ".zip"
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


SENDER = "291958900@QQ.COM"


def sendmail(toAddr: list, att_name: str, date: str):
    # 带附件的email 实例
    MESSAGE = MIMEMultipart()

    # 绑定一个正文
    MESSAGE.attach(MIMEText("encoding = 'GBK'", 'plain', "utf8"))

    # 定义一个附件
    att1 = MIMEText(open(f'{CONF.ZIP_GEN_DIR}/{att_name}', 'rb').read(), 'base64', 'utf-8')
    att1['Content-Type'] = 'application/octet-stream'
    # 设置附件1的名字
    att1['Content-Disposition'] = f'attachment; filename="{att_name}"'
    # 绑定此附件
    MESSAGE.attach(att1)
    # 设置发件人
    MESSAGE['From'] = Header("291958900@qq.com", "utf-8")
    # 设置收件人
    MESSAGE['To'] = Header(";".join(toAddr), 'utf-8')
    # 邮件的大标题
    SUBJECT = f'{date}渠道统计-结果'
    MESSAGE['Subject'] = Header(SUBJECT, "utf-8")
    try:
        smtpobj = smtplib.SMTP()
        smtpobj.connect(CONF.MAIL_HOST, 25)
        smtpobj.login(CONF.MAIL_USER, CONF.MAIL_PWD)
        smtpobj.sendmail(SENDER, toAddr, MESSAGE.as_string())
        logging.info("send email succ")
    except smtplib.SMTPException as e:
        err = f'failed: {e}'
        logging.error(err)


if __name__ == '__main__':
    # 转换一下日期,为昨天
    date = (datetime.now() + timedelta(days=CONF.DATE_OFFSET)).strftime("%Y%m%d")

    zip_file_name = makezip(f"{CONF.OUTPUT_DIR}/{date}_qry_res", CONF.ZIP_GEN_DIR, force=True)
    # sendmail(CONF.EMAIL_LIST, zip_file_name, date)
