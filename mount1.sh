#!/bin/bash

ifccd_path="//192.168.8.249/share1"
if [ $IFCCD_PATH ];then
	ifccd_path=$IFCCD_PATH
fi
echo "ifccd_path = ${ifccd_path}"

enhance_path="//192.168.8.249/share"
if [ $ENHANCE_PATH ];then
	enhance_path=$ENHANCE_PATH
fi
echo "enhance_path = ${enhance_path}"

ifccd_smb_username="ubuntu"
if [ $IFCCD_SMB_USERNAME ];then
	ifccd_smb_username=$IFCCD_SMB_USERNAME
fi
echo "ifccd_smb_username = ${ifccd_smb_username}"

ifccd_smb_passwd="1"
if [ $IFCCD_SMB_PASSWD ];then
	ifccd_smb_passwd=$IFCCD_SMB_PASSWD
fi
echo "ifccd_smb_passwd = ${ifccd_smb_passwd}"

ifccd_smb_ip="192.168.8.249"
if [ $IFCCD_SMB_IP ];then
	ifccd_smb_ip=$IFCCD_SMB_IP
fi
echo "ifccd_smb_ip = ${ifccd_smb_ip}"

enhance_smb_username="ubuntu"
if [ $ENHANCE_SMB_USERNAME ];then
	enhance_smb_username=$ENHANCE_SMB_USERNAME
fi
echo "enhance_smb_username = ${enhance_smb_username}"

enhance_smb_passwd="1"
if [ $ENHANCE_SMB_PASSWD ];then
	enhance_smb_passwd=$ENHANCE_SMB_PASSWD
fi
echo "enhance_smb_passwd = ${enhance_smb_passwd}"

enhance_smb_ip="192.168.8.249"
if [ $ENHANCE_SMB_IP ];then
	enhance_smb_ip=$ENHANCE_SMB_IP
fi
echo "enhance_smb_ip = ${enhance_smb_ip}"


smbclient -U ${ifccd_smb_username}%${ifccd_smb_passwd} -L //${ifccd_smb_ip} 
mount -t cifs ${ifccd_path} /mnt/linux_share -o username=${ifccd_smb_username},password=${ifccd_smb_passwd}
smbclient -U ${enhance_smb_username}%${enhance_smb_passwd} -L //${enhance_smb_ip}
mount -t cifs ${enhance_path} /mnt/share -o username=${enhance_smb_username},password=${enhance_smb_passwd}

echo "this is mount1.sh"
