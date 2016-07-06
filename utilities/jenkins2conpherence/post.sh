status=$(cat $3)
curl $1/api/conpherence.updatethread -d api.token=$2 -d message="$status" -d id=$4 --connect-timeout $5
